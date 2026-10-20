# """
# URL configuration for my_school project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/6.1/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('core.urls')),
#     path('students/', include('students.urls')),
#     path('academics/', include('academics.urls')),
# ]



from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from students import views as core_views

# from core.forms import (
#     CustomLoginForm, 
#     CustomPasswordResetForm, 
#     CustomSetPasswordForm
# )

def superuser_only_has_permission(request):
    return request.user.is_active and request.user.is_superuser

admin.site.has_permission = superuser_only_has_permission

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('students/', include('students.urls')),
    path('academics/', include('academics.urls')),

]

# Media routing during local development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)