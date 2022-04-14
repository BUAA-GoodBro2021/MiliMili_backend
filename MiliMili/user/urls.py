from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('findPassword/', views.findPassword),
    path('upload-avatar/', views.upload_avatar),
    path('upload-file/', views.upload_file)
]
