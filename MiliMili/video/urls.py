from django.urls import path
from . import views

urlpatterns = [
    # 视频系列
    path('upload-video', views.upload_video),
    path('del-video', views.del_video),
    path('complain-video', views.complain_video),
    # 点赞系列
    path('like', views.like_video),
    path('dislike', views.dislike_video),
    path('like-list', views.like_list),
    # 收藏系列
    path('favorite-list', views.favorite_list),
    path('favorite-simple-list', views.favorite_simple_list),
    path('create-favorite-simple', views.create_favorite_simple),
    path('create-favorite-detail', views.create_favorite_detail),
    path('del-favorite', views.del_favorite),
    path('change-favorite', views.change_favorite),
    path('collect', views.collect_video),
    path('not-collect', views.not_collect_video),
    path('collect-action', views.collect_action),
    # 评论系列
    path('add-comment', views.add_comment),
    path('del-comment', views.del_comment),
    path('reply-comment', views.reply_comment),
    path('update-comment', views.update_comment),
    path('like-comment', views.like_comment),
    path('dislike-comment', views.dislike_comment),
    # 弹幕系列
    path('add-bullet', views.add_bullet),
    path('load-bullet', views.load_bullet),
    # 视频信息及推荐
    path('detail/<str:video_id>', views.video_page)
]
