from datetime import date
from django.http import FileResponse, Http404, request
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import F, Sum, Prefetch, Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .imagekit_client import upload_to_imagekit, delete_from_imagekit
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import (
    AcademicClass, 
    Stream, 
    Section, 
    FacultyMember,  
    Subject
)
from core.models import AcademicSession
from students.models import Student, StudentEnrollment
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Permission

from .models import Banner, Notice, FormDownload, GalleryCategory, GalleryImage, CustomCampusFeature
from .forms import BannerForm, NoticeForm, FormDownloadForm, GalleryImageForm

def is_staff_check(user):
    return user.is_authenticated and (
        user.is_staff or hasattr(user, 'staff_profile')
    )

def is_staff_or_admin(user):
    """Allows access only to authenticated staff members or superusers."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def can_manage_academic_structure(user):
    """Allows superusers or staff members who have explicit model permissions."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.is_staff and (
        user.has_perm('academics.add_academicclass') or 
        user.has_perm('academics.add_section')
    )



# =====================================================================
# PUBLIC PAGES
# =====================================================================

# @login_required
# def home(request):
#     notices = Notice.objects.all()[:5]
#     streams = Stream.objects.all()
#     # Query only active banners ordered by priority
#     banners = Banner.objects.filter(is_active=True).order_by('order', '-created_at')

#     return render(request, 'home.html', {
#         'notices': notices,
#         'streams': streams,
#         'banners': banners,  # <-- Added
#     })


def about(request):
    headmaster = FacultyMember.objects.filter(designation='HM', is_active=True).first()
    streams = Stream.objects.all()
    return render(request, 'about.html', {
        'headmaster': headmaster,
        'streams': streams,
    })


@login_required
def faculty_view(request):
    headmaster = FacultyMember.objects.filter(designation='HM', is_active=True).first()
    faculty_list = FacultyMember.objects.filter(is_active=True).order_by('order', 'name')
    return render(request, 'academics/faculty.html', {
        'headmaster': headmaster,
        'faculty_list': faculty_list,
    })

def notices_view(request):
    selected_priority = (request.GET.get('priority') or '').strip()
    query = (request.GET.get('q') or '').strip()

    is_admin = is_staff_or_admin(request.user)

    # 1. Base Queryset based on role:
    if is_admin:
        # Admins see everything (including hidden ones for editing)
        notices_qs = Notice.objects.all()
    else:
        # Regular visitors & students only see active/visible notices
        notices_qs = Notice.objects.filter(is_active=True)

    # 2. Filter by priority if selected
    if selected_priority:
        notices_qs = notices_qs.filter(priority=selected_priority)

    # 3. Search query across title and content
    if query:
        notices_qs = notices_qs.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    # 4. Order by publish date and created date
    notices_qs = notices_qs.order_by('-publish_date', '-created_at')

    return render(request, 'academics/notices.html', {
        'notices': notices_qs,
        'priorities': getattr(Notice, 'PRIORITY_CHOICES', []),
        'selected_priority': selected_priority,
        'search_query': query,
        'is_admin': is_admin,
    })

# Create
@login_required
@user_passes_test(is_staff_or_admin, login_url='login')
def notice_create(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            notice = form.save()
            messages.success(request, f"Notice '{notice.title}' published successfully.")
            return redirect('notices')
    else:
        form = NoticeForm()
        
    return render(request, 'academics/notice_form.html', {'form': form, 'is_edit': False})

# Update
@login_required
@user_passes_test(is_staff_or_admin, login_url='login')
def notice_update(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, f"Notice '{notice.title}' updated successfully.")
            return redirect('notices')
    else:
        form = NoticeForm(instance=notice)

    return render(request, 'academics/notice_form.html', {'form': form, 'notice': notice, 'is_edit': True})

# Delete
@login_required
@user_passes_test(is_staff_or_admin, login_url='login')
@require_POST
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    title = notice.title
    notice.delete()
    messages.success(request, f"Notice '{title}' deleted successfully.")
    return redirect('notices')

def gallery_view(request):
    is_admin = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)

    # Automatically create default categories if table is empty
    if not GalleryCategory.objects.exists():
        default_categories = [
            ('Campus & Infrastructure', 'campus'),
            ('Labs & Classrooms', 'labs'),
            ('Events & Sports', 'events'),
        ]
        for name, slug in default_categories:
            GalleryCategory.objects.get_or_create(slug=slug, defaults={'name': name})

    if request.method == 'POST':
        if not is_admin:
            messages.error(request, "Permission denied. Staff access required.")
            return redirect(request.path)

        action = request.POST.get('action')

        # 1. UPLOAD IMAGE
        if action == 'upload_image':
            title = request.POST.get('title', '').strip()
            category_id = request.POST.get('category_id')
            image_file = request.FILES.get('image')
            caption = request.POST.get('caption', '').strip()
            is_featured = request.POST.get('is_featured') == 'on'

            if title and category_id and image_file:
                try:
                    category = get_object_or_404(GalleryCategory, id=category_id)
                    ik_data = upload_to_imagekit(image_file, image_file.name, folder="/gallery")

                    GalleryImage.objects.create(
                        title=title,
                        category=category,
                        image_url=ik_data['url'],
                        imagekit_file_id=ik_data['file_id'],
                        caption=caption,
                        is_featured=is_featured
                    )
                    messages.success(request, f"Photo '{title}' uploaded successfully!")
                except Exception as e:
                    messages.error(request, f"Upload failed: {str(e)}")
            else:
                messages.error(request, "Title, Category, and Image file are required.")
            return redirect(request.path)

        # 2. EDIT IMAGE
        elif action == 'edit_image':
            image_id = request.POST.get('image_id')
            photo = get_object_or_404(GalleryImage, id=image_id)

            photo.title = request.POST.get('title', photo.title).strip()
            category_id = request.POST.get('category_id')
            if category_id:
                photo.category = get_object_or_404(GalleryCategory, id=category_id)

            photo.caption = request.POST.get('caption', '').strip()
            photo.is_featured = request.POST.get('is_featured') == 'on'

            if 'image' in request.FILES:
                try:
                    delete_from_imagekit(photo.imagekit_file_id)
                    new_file = request.FILES['image']
                    ik_data = upload_to_imagekit(new_file, new_file.name, folder="/gallery")
                    photo.image_url = ik_data['url']
                    photo.imagekit_file_id = ik_data['file_id']
                except Exception as e:
                    messages.error(request, f"Image replacement failed: {str(e)}")

            photo.save()
            messages.success(request, f"Photo '{photo.title}' updated successfully!")
            return redirect(request.path)

        # 3. DELETE IMAGE
        elif action == 'delete_image':
            image_id = request.POST.get('target_id')
            photo = get_object_or_404(GalleryImage, id=image_id)
            title = photo.title

            delete_from_imagekit(photo.imagekit_file_id)
            photo.delete()

            messages.success(request, f"Photo '{title}' removed.")
            return redirect(request.path)

    # Query all categories with their images pre-fetched
    categories = GalleryCategory.objects.all().prefetch_related('images')
    images = GalleryImage.objects.select_related('category').all().order_by('-created_at')

    return render(request, 'gallery_2.html', {
        'categories': categories,
        'images': images,
        'is_admin': is_admin,
    })

# 1. READ (List view)
def downloads_view(request):
    category = request.GET.get('category', '').strip()
    query = request.GET.get('q', '').strip()

    downloads_qs = FormDownload.objects.all().order_by('-uploaded_at')

    # Hide inactive documents for regular visitors
    if not is_staff_or_admin(request.user):
        downloads_qs = downloads_qs.filter(is_active=True)

    if category:
        downloads_qs = downloads_qs.filter(category=category)

    if query:
        downloads_qs = downloads_qs.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    return render(
        request,
        'academics/downloads.html',
        {
            'downloads': downloads_qs,
            'categories': FormDownload.CATEGORY_CHOICES,
            'selected_category': category,
            'search_query': query,
            'is_admin': is_staff_or_admin(request.user),
        },
    )


# 2. CREATE
@login_required
@user_passes_test(is_staff_or_admin, login_url='login')
def download_create(request):
    if request.method == 'POST':
        # Removed request.FILES since Google Drive link is used
        form = FormDownloadForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(
                request, f"Document '{item.title}' linked successfully."
            )
            return redirect('downloads')
    else:
        form = FormDownloadForm()

    return render(
        request, 'academics/download_form.html', {'form': form, 'is_edit': False}
    )


# 3. UPDATE
@login_required
@user_passes_test(is_staff_or_admin, login_url='login')
def download_update(request, pk):
    item = get_object_or_404(FormDownload, pk=pk)
    if request.method == 'POST':
        # Removed request.FILES since Google Drive link is used
        form = FormDownloadForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"Document '{item.title}' updated successfully.")
            return redirect('downloads')
    else:
        form = FormDownloadForm(instance=item)

    return render(
        request,
        'academics/download_form.html',
        {'form': form, 'item': item, 'is_edit': True},
    )


# 4. DELETE
@login_required
@user_passes_test(is_staff_or_admin, login_url='login')
@require_POST
def download_delete(request, pk):
    item = get_object_or_404(FormDownload, pk=pk)
    title = item.title
    item.delete()
    messages.success(request, f"Document '{title}' deleted successfully.")
    return redirect('downloads')


# 5. TRACK & REDIRECT TO GOOGLE DRIVE
def track_download_file(request, pk):
    item = get_object_or_404(FormDownload, pk=pk)
    if not item.drive_link:
        raise Http404('Google Drive file link not configured.')

    # Increment counter atomically
    FormDownload.objects.filter(pk=pk).update(
        download_count=F('download_count') + 1
    )

    # Redirect directly to Google Drive download/view link
    target_url = item.direct_download_url or item.drive_link
    return redirect(target_url)


def contact_view(request):
    submitted = request.method == 'POST'
    return render(request, 'contact.html', {'submitted': submitted})


def can_manage_academic_structure(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def seed_session_structure(session_obj):
    """
    Creates standard Classes (9-12), Streams, and Sections for the given session.
    """
    if not session_obj:
        return

    # 1. Ensure Streams Exist
    stream_sci, _ = Stream.objects.get_or_create(
        code='SCIENCE',
        defaults={
            'name': 'Science (PCM/PCB)',
            'faculty': 'SCIENCE',
            'sanctioned_seats': 60,
            'description': 'Physics, Chemistry, Mathematics, Biology',
        }
    )
    stream_arts, _ = Stream.objects.get_or_create(
        code='ARTS',
        defaults={
            'name': 'Arts (I.A)',
            'faculty': 'ARTS',
            'sanctioned_seats': 60,
            'description': 'History, Political Science, Geography, Economics',
        }
    )

    # 2. Ensure Academic Classes Exist
    c9, _ = AcademicClass.objects.get_or_create(
        numeric_level=9,
        defaults={'name': 'Class IX (Secondary Foundation)', 'is_intermediate': False}
    )
    c10, _ = AcademicClass.objects.get_or_create(
        numeric_level=10,
        defaults={'name': 'Class X (Secondary Board)', 'is_intermediate': False}
    )
    c11, _ = AcademicClass.objects.get_or_create(
        numeric_level=11,
        defaults={'name': 'Class XI (Senior Secondary)', 'is_intermediate': True}
    )
    c12, _ = AcademicClass.objects.get_or_create(
        numeric_level=12,
        defaults={'name': 'Class XII (Senior Secondary Terminal)', 'is_intermediate': True}
    )

    # 3. Blueprint: (Class, Name, Stream, Capacity)
    sections_blueprint = [
        (c9, 'A', None, 40),
        (c9, 'B', None, 40),
        (c10, 'A', None, 40),
        (c10, 'B', None, 40),
        (c11, 'A - Science', stream_sci, 60),
        (c11, 'A - Arts', stream_arts, 60),
        (c12, 'A - Science', stream_sci, 60),
        (c12, 'A - Arts', stream_arts, 60),
    ]

    for cls_obj, s_name, stream_obj, cap in sections_blueprint:
        sec = Section.objects.filter(session=session_obj, academic_class=cls_obj, name=s_name).first()
        if not sec:
            Section.objects.create(
                session=session_obj,
                academic_class=cls_obj,
                name=s_name,
                stream=stream_obj,
                capacity=cap
            )
        else:
            if stream_obj and sec.stream != stream_obj:
                sec.stream = stream_obj
                sec.save(update_fields=['stream'])


@login_required
@user_passes_test(can_manage_academic_structure, login_url='/admin/login/')
def manage_academic_structure(request):
    # Retrieve session ID from POST first, then GET query string
    session_param = request.POST.get('session_id') or request.GET.get('session') or ''

    def redirect_with_session(target_id=None):
        base_url = reverse('manage_academic_structure')
        sid = target_id or session_param
        if sid:
            return redirect(f"{base_url}?session={sid}")
        return redirect('manage_academic_structure')

    # -------------------------------------------------------------
    # POST ACTIONS
    # -------------------------------------------------------------
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'seed_default_structure':
            # Target the session explicitly sent by the button form
            target_sess_id = request.POST.get('session_id') or session_param
            target_sess = AcademicSession.objects.filter(id=target_sess_id).first() if target_sess_id else None

            if not target_sess:
                target_sess = AcademicSession.objects.filter(is_current=True).first() or AcademicSession.objects.first()

            if target_sess:
                with transaction.atomic():
                    seed_session_structure(target_sess)
                messages.success(request, f"Standard sections generated for Academic Session {target_sess.name}!")
                return redirect_with_session(target_sess.id)
            else:
                messages.error(request, "No active session found to seed.")
            return redirect_with_session()

        elif action == 'create_session':
            name = request.POST.get('session_name', '').strip()
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            if name and start_date and end_date:
                try:
                    with transaction.atomic():
                        new_session = AcademicSession.objects.create(
                            name=name,
                            start_date=start_date,
                            end_date=end_date
                        )
                        # Automatically seed predefined classes & sections for the new session
                        seed_session_structure(new_session)

                    messages.success(request, f"Session '{name}' created with standard classes and sections.")
                    # Keep the newly created session active
                    return redirect_with_session(new_session.id)
                except IntegrityError:
                    messages.error(request, f"Session '{name}' already exists.")
            else:
                messages.error(request, "Session name, start date, and end date are required.")
            return redirect_with_session()

        elif action == 'create_section':
            class_id = request.POST.get('class_id')
            session_id = request.POST.get('session_id') or session_param
            sec_name = request.POST.get('section_name', '').strip()
            stream_id = request.POST.get('stream_id') or None
            room_number = request.POST.get('room_number', '').strip()

            try:
                capacity = int(request.POST.get('capacity') or 40)
            except ValueError:
                capacity = 40

            if not session_id or not class_id or not sec_name:
                messages.error(request, "Class, Section Name, and Session are required.")
                return redirect_with_session(session_id)

            try:
                Section.objects.create(
                    session_id=session_id,
                    academic_class_id=class_id,
                    name=sec_name,
                    stream_id=stream_id,
                    room_number=room_number,
                    capacity=capacity
                )
                messages.success(request, f"Section '{sec_name}' created.")
            except IntegrityError:
                messages.error(request, "A section with this name already exists for this class.")
            return redirect_with_session(session_id)

        elif action == 'update_section':
            sec_id = request.POST.get('section_id')
            sec = get_object_or_404(Section, id=sec_id)
            sec.academic_class_id = request.POST.get('class_id') or sec.academic_class_id
            sec.name = request.POST.get('section_name', '').strip()
            sec.stream_id = request.POST.get('stream_id') or None
            sec.room_number = request.POST.get('room_number', '').strip()

            try:
                sec.capacity = int(request.POST.get('capacity') or sec.capacity)
            except ValueError:
                pass

            sess_id = request.POST.get('session_id') or sec.session_id
            sec.session_id = sess_id

            try:
                sec.save()
                messages.success(request, f"Section '{sec.name}' updated.")
            except IntegrityError:
                messages.error(request, "Section conflicts with an existing record.")
            return redirect_with_session(sec.session_id)

        elif action == 'delete_section':
            sec_id = request.POST.get('target_id')
            sec = get_object_or_404(Section, id=sec_id)
            preserved_session_id = sec.session_id
            
            # Deletes ONLY this specific section row for this session
            sec.delete()
            
            messages.success(request, "Section removed from this session.")
            return redirect_with_session(preserved_session_id)

        elif action == 'create_class':
            name = request.POST.get('name', '').strip()
            is_intermediate = request.POST.get('is_intermediate') == 'on'
            try:
                num_level = int(request.POST.get('numeric_level', 0))
                AcademicClass.objects.create(
                    numeric_level=num_level,
                    name=name,
                    is_intermediate=is_intermediate
                )
                messages.success(request, f"Class '{name}' created.")
            except (ValueError, TypeError):
                messages.error(request, "Invalid numeric level provided.")
            except IntegrityError:
                messages.error(request, f"Class level {request.POST.get('numeric_level')} already exists.")
            return redirect_with_session()

        elif action == 'update_class':
            cls_id = request.POST.get('class_id')
            cls_obj = get_object_or_404(AcademicClass, id=cls_id)
            try:
                cls_obj.numeric_level = int(request.POST.get('numeric_level', cls_obj.numeric_level))
                cls_obj.name = request.POST.get('name', '').strip()
                cls_obj.is_intermediate = request.POST.get('is_intermediate') == 'on'
                cls_obj.save()
                messages.success(request, f"Class '{cls_obj.name}' updated.")
            except (ValueError, TypeError):
                messages.error(request, "Invalid numeric level.")
            except IntegrityError:
                messages.error(request, "Another class already has that numeric level.")
            return redirect_with_session()

        elif action == 'delete_class':
            cls_id = request.POST.get('target_id')
            session_id = request.POST.get('session_id') or session_param
            cls_obj = get_object_or_404(AcademicClass, id=cls_id)
            
            if session_id:
                # ONLY delete sections of this class for THIS specific session
                deleted_count, _ = Section.objects.filter(
                    academic_class=cls_obj,
                    session_id=session_id
                ).delete()
                messages.success(request, f"Removed sections for '{cls_obj.name}' in this session ({deleted_count} removed). Other sessions remain untouched.")
            else:
                messages.error(request, "No active session specified.")
                
            return redirect_with_session()

        elif action == 'create_stream':
            try:
                seats = int(request.POST.get('sanctioned_seats') or 60)
                Stream.objects.create(
                    name=request.POST.get('stream_name', '').strip(),
                    code=request.POST.get('stream_code', '').strip().upper(),
                    faculty=request.POST.get('faculty', 'SCIENCE'),
                    sanctioned_seats=seats,
                    description=request.POST.get('stream_desc', '').strip()
                )
                messages.success(request, "Stream registered.")
            except IntegrityError:
                messages.error(request, "A stream with this code already exists.")
            return redirect_with_session()

        elif action == 'update_stream':
            st = get_object_or_404(Stream, id=request.POST.get('stream_id'))
            st.name = request.POST.get('stream_name', '').strip()
            st.code = request.POST.get('stream_code', '').strip().upper()
            st.faculty = request.POST.get('faculty', 'SCIENCE')
            try:
                st.sanctioned_seats = int(request.POST.get('sanctioned_seats') or st.sanctioned_seats)
            except ValueError:
                pass
            st.description = request.POST.get('stream_desc', '').strip()
            st.save()
            messages.success(request, f"Stream '{st.name}' updated.")
            return redirect_with_session()

        elif action == 'delete_stream':
            st = get_object_or_404(Stream, id=request.POST.get('target_id'))
            st.delete()
            messages.success(request, "Stream removed.")
            return redirect_with_session()

    # -------------------------------------------------------------
    # GET / DISPLAY DATA
    # -------------------------------------------------------------
    sessions = AcademicSession.objects.all().order_by('-start_date')
    selected_session_id = request.GET.get('session')

    active_session = None
    if selected_session_id:
        active_session = sessions.filter(id=selected_session_id).first()
    if not active_session:
        active_session = sessions.filter(is_current=True).first() or sessions.first()

    # Get all active sections for this session
    active_sections = list(
        Section.objects.filter(session=active_session).select_related('stream')
    ) if active_session else []

    # Get all classes
    all_classes = list(AcademicClass.objects.all().order_by('numeric_level'))

    # Attach sections to each class
    session_classes = []
    for c in all_classes:
        c.active_sections = [s for s in active_sections if s.academic_class_id == c.id]
        c.active_sections_count = len(c.active_sections)
        
        # ONLY include the class in the display if it actually has sections in this session!
        if c.active_sections_count > 0:
            session_classes.append(c)

    streams = Stream.objects.all()
    science_seats = streams.filter(faculty='SCIENCE').aggregate(s=Sum('sanctioned_seats'))['s'] or 0
    arts_seats = streams.filter(faculty='ARTS').aggregate(s=Sum('sanctioned_seats'))['s'] or 0

    inter_sec_filter = Q(academic_class__is_intermediate=True)
    if active_session:
        inter_sec_filter &= Q(session=active_session)
    total_intermediate_capacity = Section.objects.filter(inter_sec_filter).aggregate(c=Sum('capacity'))['c'] or 0

    is_initialized = len(active_sections) > 0

    return render(request, 'academics/manage_academic_structure.html', {
        'classes': session_classes,   # <--- PASS ONLY CLASSES THAT HAVE SECTIONS
        'streams': streams,
        'sessions': sessions,
        'active_session': active_session,
        'total_sections_count': len(active_sections),
        'science_seats': science_seats,
        'arts_seats': arts_seats,
        'total_intermediate_capacity': total_intermediate_capacity,
        'is_initialized': is_initialized,
    })


# =====================================================================
# MODAL QUICK-ACTION ENDPOINTS
# =====================================================================

@login_required
@user_passes_test(is_staff_or_admin, login_url='/admin/login/')
def edit_section(request, section_id):
    sec = get_object_or_404(Section, id=section_id)
    if request.method == "POST":
        sec.name = request.POST.get("section_name", "").strip().upper()
        sec.capacity = int(request.POST.get("capacity") or 40)
        sec.stream_id = request.POST.get("stream_id") or None
        sec.room_number = request.POST.get("room_number", "").strip()
        try:
            sec.save()
            messages.success(request, f"Section {sec.name} updated.")
        except IntegrityError:
            messages.error(request, "Failed to update: A conflicting section already exists.")
    return redirect('manage_academic_structure')


@login_required
@user_passes_test(is_staff_or_admin, login_url='/admin/login/')
def delete_section(request, section_id):
    sec = get_object_or_404(Section, id=section_id)
    sec.delete()
    messages.success(request, "Section removed.")
    return redirect('manage_academic_structure')


@login_required
@user_passes_test(is_staff_or_admin, login_url='/admin/login/')
def edit_stream(request, stream_id):
    st = get_object_or_404(Stream, id=stream_id)
    if request.method == "POST":
        st.name = request.POST.get("stream_name", "").strip()
        st.code = request.POST.get("stream_code", "").strip().upper()
        st.faculty = request.POST.get("faculty", st.faculty)
        st.sanctioned_seats = int(request.POST.get("sanctioned_seats") or st.sanctioned_seats)
        st.description = request.POST.get("stream_desc", "").strip()
        try:
            st.save()
            messages.success(request, f"Stream {st.name} updated.")
        except IntegrityError:
            messages.error(request, "Stream with that code already exists.")
    return redirect('manage_academic_structure')


@login_required
@user_passes_test(is_staff_or_admin, login_url='/admin/login/')
def delete_stream(request, stream_id):

    st = get_object_or_404(Stream, id=stream_id)
    st.delete()
    messages.success(request, "Stream removed.")
    return redirect('manage_academic_structure')


def is_superuser_check(user):
    return user.is_authenticated and user.is_superuser


def can_manage_academic_structure(user):
    """Allows superusers or staff members who have explicit model permissions."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.is_staff and (
        user.has_perm('academics.add_academicclass') or 
        user.has_perm('academics.add_section')
    )


# ------------------------------------------------------------------
# SUPERUSER-ONLY: Manage Staff Academic Permissions
# ------------------------------------------------------------------
@user_passes_test(is_superuser_check, login_url='/admin/login/')
def manage_staff_permissions(request):

    """List all staff users and toggle their ability to manage academic structure."""
    staff_users = User.objects.filter(is_staff=True).exclude(is_superuser=True).order_by('username')
    
    # Target permissions
    class_ct = ContentType.objects.get_for_model(AcademicClass)
    section_ct = ContentType.objects.get_for_model(Section)
    
    academic_perms = Permission.objects.filter(
        content_type__in=[class_ct, section_ct],
        codename__in=['add_academicclass', 'change_academicclass', 'add_section', 'change_section']
    )

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('perm_action')  # 'grant' or 'revoke'
        target_user = get_object_or_404(User, id=user_id, is_staff=True)

        if action == 'grant':
            target_user.user_permissions.add(*academic_perms)
            messages.success(request, f"Academic management permissions granted to {target_user.username}.")
        elif action == 'revoke':
            target_user.user_permissions.remove(*academic_perms)
            messages.info(request, f"Academic management permissions revoked from {target_user.username}.")

        return redirect('manage_staff_permissions')

    # Prepare list with flag indicating whether permission is granted
    staff_data = []
    for staff in staff_users:
        has_perm = staff.has_perm('academics.add_academicclass') and staff.has_perm('academics.add_section')
        staff_data.append({
            'user': staff,
            'can_manage': has_perm,
        })

    return render(request, 'academics/manage_staff_permissions.html', {

        'staff_data': staff_data,
    })




def home_view(request):
    """Public home view displaying active banners, latest notices, and featured gallery items."""
    banners = Banner.objects.filter(is_active=True).order_by('order', '-created_at')
    notices = Notice.objects.filter(is_active=True)[:5]
    featured_photos = GalleryImage.objects.filter(is_featured=True)[:6]
    downloads = FormDownload.objects.filter(is_active=True)[:4]
    custom_features = CustomCampusFeature.objects.filter(is_active=True).order_by('order', '-created_at')

    return render(request, 'home.html', {
        'banners': banners,
        'notices': notices,
        'featured_photos': featured_photos,
        'downloads': downloads,
        'facilities': custom_features,
    })

def downloads(request):
    category = request.GET.get('category', '').strip()
    downloads = FormDownload.objects.filter(is_active=True)

    if category:
        downloads = downloads.filter(category=category)

    return render(request, 'downloads.html', {
        'downloads': downloads,
        'category_choices': FormDownload.CATEGORY_CHOICES,
        'selected_category': category,
    })


# =====================================================================
# BANNER CRUD & VISIBILITY VIEWS
# =====================================================================


@login_required
@user_passes_test(is_staff_check, login_url='login')
def banner_manage_list(request):
    """Admin table to view, edit, toggle visibility, and delete all banners."""
    banners = Banner.objects.all().order_by('order', '-created_at')
    return render(request, 'portal/banner_manage.html', {'banners': banners})


@login_required
@user_passes_test(is_staff_check, login_url='login')
def banner_create(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES.get('image')
            try:
                # 1. Upload file directly to ImageKit.io
                ik_data = upload_to_imagekit(image_file, image_file.name, folder="/banners")

                # 2. Save model instance with ImageKit CDN details
                banner = form.save(commit=False)
                banner.image_url = ik_data['url']
                banner.imagekit_file_id = ik_data['file_id']
                banner.save()

                messages.success(request, "Banner created and uploaded to ImageKit successfully.")
                return redirect('banner_manage')
            except Exception as e:
                messages.error(request, f"ImageKit upload failed: {str(e)}")
    else:
        form = BannerForm()
    return render(request, 'portal/banner_form.html', {'form': form, 'is_edit': False})


@login_required
@user_passes_test(is_staff_check, login_url='login')
def banner_update(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            # If user selected a replacement image
            if 'image' in request.FILES:
                try:
                    # 1. Remove previous file from ImageKit
                    delete_from_imagekit(banner.imagekit_file_id)

                    # 2. Upload replacement image
                    new_file = request.FILES['image']
                    ik_data = upload_to_imagekit(new_file, new_file.name, folder="/banners")

                    banner.image_url = ik_data['url']
                    banner.imagekit_file_id = ik_data['file_id']
                except Exception as e:
                    messages.error(request, f"ImageKit replacement error: {str(e)}")
                    return render(request, 'portal/banner_form.html', {'form': form, 'banner': banner, 'is_edit': True})

            form.save()
            messages.success(request, f"Banner '{banner.title}' updated successfully.")
            return redirect('banner_manage')
    else:
        form = BannerForm(instance=banner)
    return render(request, 'portal/banner_form.html', {'form': form, 'banner': banner, 'is_edit': True})


@login_required
@user_passes_test(is_staff_check, login_url='login')
@require_POST
def banner_toggle_status(request, pk):
    """Fast AJAX or POST endpoint to show/hide without deleting."""
    banner = get_object_or_404(Banner, pk=pk)
    banner.is_active = not banner.is_active
    banner.save(update_fields=['is_active'])

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'is_active': banner.is_active})

    messages.info(request, f"Banner status changed to {'Visible' if banner.is_active else 'Hidden'}.")
    return redirect('banner_manage')


@login_required
@user_passes_test(is_staff_check, login_url='login')
@require_POST
def banner_delete(request, pk):
    """Deletes banner from both the database and ImageKit.io storage."""
    banner = get_object_or_404(Banner, pk=pk)
    title = banner.title

    # 1. Remove file from ImageKit.io CDN
    delete_from_imagekit(banner.imagekit_file_id)

    # 2. Delete database record
    banner.delete()

    messages.success(request, f"Banner '{title}' deleted from database and ImageKit.io.")
    return redirect('banner_manage')

