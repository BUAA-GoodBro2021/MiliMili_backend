from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('register',views.register),
    # path('login/',views.login_view),
    # path('sendEmail/',views.email_view),
    # path('change-or-findPassword/',views.change_or_find_password_view)
]