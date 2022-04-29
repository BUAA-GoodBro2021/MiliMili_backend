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
    path('video-list', views.video_list),
    path('all-list', views.all_list),

    path('up-follow-list', views.up_follow_list),
    path('up-fan-list', views.up_fan_list),
    path('up-video-list', views.up_video_list),
    path('up-all-list', views.up_all_list),
]
