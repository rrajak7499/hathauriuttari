from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from core.models import SchoolContactInfo, AcademicSession
from academics.models import Banner, Notice, FormDownload, GalleryCategory
from students.views import seed_session_structure
import setup_config

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds or replicates the school portal from setup_config.py"

    def handle(self, *args, **options):
        cfg = setup_config.SCHOOL_CONFIG
        self.stdout.write(self.style.NOTICE(f"Initializing instance for: {cfg['school_name']}..."))

        with transaction.atomic():
            # 1. School Profile
            SchoolContactInfo.objects.update_or_create(
                id=1,
                defaults={
                    "school_name": cfg["school_name"],
                    "address": cfg["address"],
                    "primary_phone": cfg["primary_phone"],
                    "email": cfg["email"],
                    "office_hours": cfg["office_hours"],
                    "map_location_query": cfg["map_location_query"],
                }
            )
            self.stdout.write(self.style.SUCCESS("✓ School contact & branding updated."))

            # 2. Administrator User
            admin_user, created = User.objects.get_or_create(
                username=cfg["admin_username"],
                defaults={
                    "email": cfg["admin_email"],
                    "first_name": cfg["admin_full_name"],
                    "is_staff": True,
                    "is_superuser": True,
                }
            )
            admin_user.set_password(cfg["admin_password"])
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"✓ {action} Superadmin: {cfg['admin_username']}"))

            # 3. Academic Session & Grade Matrix
            s_start = datetime.strptime(cfg["session_start"], "%Y-%m-%d").date()
            s_end = datetime.strptime(cfg["session_end"], "%Y-%m-%d").date()
            
            session, _ = AcademicSession.objects.get_or_create(
                name=cfg["session_name"],
                defaults={
                    "start_date": s_start,
                    "end_date": s_end,
                    "is_current": True,
                    "allow_modifications": True,
                }
            )
            if cfg.get("seed_standard_classes"):
                seed_session_structure(session)
                self.stdout.write(self.style.SUCCESS("✓ Seeded academic classes (9th–12th) & stream structures."))

            # 4. Hero Banners
            for b_data in cfg.get("banners", []):
                Banner.objects.update_or_create(
                    title=b_data["title"],
                    defaults={
                        "image_url": b_data["image_url"],
                        "order": b_data.get("order", 0),
                        "is_active": b_data.get("is_active", True),
                    }
                )
            self.stdout.write(self.style.SUCCESS(f"✓ Seeded {len(cfg.get('banners', []))} banners."))

            # 5. Public Notices
            for n_data in cfg.get("notices", []):
                Notice.objects.update_or_create(
                    title=n_data["title"],
                    defaults={
                        "content": n_data.get("content", ""),
                        "priority": n_data.get("priority", "normal"),
                        "drive_link": n_data.get("drive_link", ""),
                        "is_active": n_data.get("is_active", True),
                    }
                )
            self.stdout.write(self.style.SUCCESS(f"✓ Seeded {len(cfg.get('notices', []))} notices."))

            # 6. Forms & Downloads
            for d_data in cfg.get("downloads", []):
                FormDownload.objects.update_or_create(
                    title=d_data["title"],
                    defaults={
                        "category": d_data.get("category", "admission"),
                        "drive_link": d_data.get("drive_link", ""),
                        "description": d_data.get("description", ""),
                        "is_active": d_data.get("is_active", True),
                    }
                )
            self.stdout.write(self.style.SUCCESS(f"✓ Seeded {len(cfg.get('downloads', []))} download items."))

            # 7. Standard Media Categories
            for name, slug in [('Campus & Grounds', 'campus'), ('Laboratories', 'labs'), ('Sports & Cultural', 'events')]:
                GalleryCategory.objects.get_or_create(slug=slug, defaults={'name': name})

        self.stdout.write(self.style.SUCCESS(f"\n🚀 System setup complete for {cfg['school_name']}!"))