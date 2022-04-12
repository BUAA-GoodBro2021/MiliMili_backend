from django.urls import path
from . import views
from django.urls import path

from . import views

urlpatterns = [
    path('<str:url>', views.active),
    path('read-message/<int:message_id>', views.read_message),
    path('del-message/<int:message_id>', views.del_message),
    # path('sendEmail/',views.email_view),
    # path('change-or-findPassword/',views.change_or_find_password_view)
]
