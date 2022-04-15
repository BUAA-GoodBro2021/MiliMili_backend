from django.urls import path

from . import views

urlpatterns = [
    path('upload-video', views.upload_video),

]
