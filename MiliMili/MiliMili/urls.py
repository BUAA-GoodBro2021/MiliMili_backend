"""MiliMili URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

urlpatterns = [
    path('api/admin', admin.site.urls),
    path('api/user/', include('user.urls')),
    path('api/sending/', include('sending.urls')),
    path('api/bucket_manager/', include('bucket_manager.urls')),
    # re_path('^media/(?P<path>.*?)$', serve, kwargs={'document_root': settings.MEDIA_ROOT})
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
