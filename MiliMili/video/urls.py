from django.urls import path

from . import views

urlpatterns = [
    path('upload-video', views.upload_video),
    path('like-video', views.like_video),
    path('dislike-video', views.dislike_video),
]
