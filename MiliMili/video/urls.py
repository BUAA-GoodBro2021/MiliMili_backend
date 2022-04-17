from django.urls import path

from . import views

urlpatterns = [
    path('upload-video', views.upload_video),
    # 点赞系列
    path('like', views.like_video),
    path('dislike', views.dislike_video),
    path('like-list', views.like_list),
]
