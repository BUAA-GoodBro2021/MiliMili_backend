from django.urls import path
from . import views

urlpatterns = [
    path('video/<str:search_str>', views.video_search),
    path('user/<str:search_str>', views.user_search),
    path('tag/<str:search_str>', views.tag_search),
]
