from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register),
    path('login', views.login),
    path('findPassword', views.findPassword),

    path('upload-avatar', views.upload_avatar),
    path('change-file', views.change_file),

    path('follow', views.follow),
    path('unfollow', views.unfollow),
    path('follow-list', views.follow_list),
    path('fan-list', views.fan_list),
]
