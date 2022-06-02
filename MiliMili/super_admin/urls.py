from django.urls import path
from . import views

urlpatterns = [
    # 视频系列
    path('video-list', views.all_list),
    path('audit-video-list', views.audit_verify_video_list),

    # 审核系列
    path('audit-video', views.audit_video),
    path('redo-audit-video', views.redo_audit_video),
    path('verify-complain-video', views.verify_complain_video),

    # 加载主页系列
    path('load-index', views.load_index)
]
