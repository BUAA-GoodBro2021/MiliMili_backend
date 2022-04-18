from django.urls import path

from . import views

urlpatterns = [
    # 视频系列
    path('upload-video', views.upload_video),
    path('del-video', views.del_video),
    # 点赞系列
    path('like', views.like_video),
    path('dislike', views.dislike_video),
    path('like-list', views.like_list),
    # 收藏系列
    path('favorite-list', views.favorite_list),
    path('create-favorite', views.create_favorite),
    path('del-favorite', views.del_favorite),
    path('change-favorite', views.change_favorite),
    path('collect', views.collect_video),
    path('not-collect', views.not_collect_video),
]
