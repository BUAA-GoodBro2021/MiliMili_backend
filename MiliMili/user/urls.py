from django.urls import path
from . import views
from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register),
    path('login', views.login),
    path('findPassword', views.findPassword)
]
