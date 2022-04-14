from django.urls import path
from . import views
from django.urls import path

from . import views

urlpatterns = [
    path('<str:url>/', views.active),
    path('read-message/<int:message_id>/', views.read_message),
    path('read-message/all/', views.read_all_message),
    path('del-message/<int:message_id>/', views.del_message),
    path('del-message/all/', views.del_all_message),
    # path('sendEmail/',views.email_view),
    # path('change-or-findPassword/',views.change_or_find_password_view)
]
