from django.urls import path
from . import views

urlpatterns = [
    path('', views.recommend_video),
    path('video', views.video_search),
    path('user', views.user_search),
    path('zone/<str:zone>', views.zone_search)
]
