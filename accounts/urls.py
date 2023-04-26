from django.urls import path
from accounts import views

app_name = 'users'

urlpatterns = [
    path('register-user/', views.register_user, name='register-user'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    
    
    path('login-user/', views.login_user, name='login-user'),
    path('logout-user/', views.logout_user, name='logout-user'),
    
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),
    
    path('forgot-password/', views.forgotPassword, name='forgot-password'),
    path('reset-password-validate/<uidb64>/<token>/', views.reset_password_validate, name='reset-password-validate'),
    path('reset-password-page/', views.reset_password_page, name='reset-password-page')

    
]
