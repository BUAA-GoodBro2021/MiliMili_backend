from django.urls import path
from . import views
from django.urls import path

from . import views

urlpatterns = [
    path('<str:url>', views.active),
    path('station-message/<int:message_id>', views.read_message),
    # path('sendEmail/',views.email_view),
    # path('change-or-findPassword/',views.change_or_find_password_view)
]
