"""digibuddies URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
import notifications.urls

from django.conf.urls import handler404,handler500

handler404 = "mainapp.views.page_not_found_view"


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('mainapp.urls')),
    path('accounts/',include('allauth.urls')),
    path('seller',include('seller.urls')),
    path('buyer',include('buyer.urls')),
    path('',include('chat.urls')),
    re_path(r'^webpush/', include('webpush.urls')),
    re_path(r"^ckeditor/", include("ckeditor_uploader.urls")),
    re_path(r'^inbox/notifications/', include(notifications.urls, namespace='notifications')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
