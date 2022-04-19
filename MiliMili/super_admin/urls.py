from django.urls import path
from . import views

urlpatterns = [
    # 视频系列
    path('list', views.need_verify_video_list),

]
