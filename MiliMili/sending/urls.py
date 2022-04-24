from django.urls import path
from . import views
from django.urls import path

from . import views

urlpatterns = [
    path('<str:url>', views.active),
    path('read-message/detail', views.read_message),
    path('read-message/all', views.read_all_message),
    path('del-message/detail', views.del_message),
    path('del-message/all', views.del_all_message),
    path('message/send-message', views.send_message),
]
