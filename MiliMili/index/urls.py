from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_message),
    path('video', views.video_search),
    path('user', views.user_search),
    path('zone/<str:zone>', views.zone_search),
    path('ip_address', views.get_ip_address),
]
