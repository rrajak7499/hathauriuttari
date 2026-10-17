from django import forms
from .models import Banner, Notice, FormDownload, GalleryImage


TW_INPUT = "w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
TW_SELECT = "w-full text-xs font-medium bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"

class BannerForm(forms.ModelForm):
    # Standalone file field for ImageKit upload (not in the database model)
    image = forms.ImageField(
        required=True,
        help_text="Select a banner image to upload to ImageKit.io"
    )

    class Meta:
        model = Banner
        # ONLY list fields that exist on your Banner model:
        fields = ['title', 'order', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # When editing an existing banner, replacing the image is optional
        if self.instance and self.instance.pk:
            self.fields['image'].required = False


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'priority', 'drive_link', 'publish_date', 'expires_at', 'is_active']
        widgets = {
            'drive_link': forms.URLInput(attrs={
                'placeholder': 'https://drive.google.com/file/d/.../view?usp=sharing',
                'class': 'w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs text-slate-800'
            }),
        }

class FormDownloadForm(forms.ModelForm):
    class Meta:
        model = FormDownload
        fields = ['title', 'category', 'drive_link', 'description', 'is_active']
        widgets = {
            'drive_link': forms.URLInput(attrs={
                'placeholder': 'https://drive.google.com/file/d/.../view?usp=sharing',
                'class': 'w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs text-slate-800'
            }),
        }
        
class GalleryImageForm(forms.ModelForm):
    # Declare 'image' as a standard form file field (not a database model field)
    image = forms.ImageField(
        required=True,
        help_text="Select an image file to upload to ImageKit.io"
    )

    class Meta:
        model = GalleryImage
        # Exclude 'image' from model fields, include model fields only:
        fields = ['title', 'category', 'caption', 'is_featured']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If updating an existing record, the file is not mandatory
        if self.instance and self.instance.pk:
            self.fields['image'].required = False



