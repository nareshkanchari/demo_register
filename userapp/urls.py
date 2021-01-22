from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('', index, name="index"),
    path('login/', loginpage, name="login"),
    path('login_mobile/', login_mobile, name='login_mobile'),
    path('login_otp/', login_otp, name="login_otp"),
    path('home/', userhome, name='userhome'),
    path('register/', registerPage, name='register'),
    path('logout/', logoutpage, name='logout'),
    path('verify_mobile/', verify_mobile, name="verify_mobile"),
    path('emailverification/', emailverification, name='emailverification'),
    path('useremailhome/', useremailhome, name='useremailhome'),

    path('reset_password/',
         auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
         name="reset_password"),

    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_sent.html"),
         name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_form.html"),
         name="password_reset_confirm"),

    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_done.html"),
         name="password_reset_complete"),

]
