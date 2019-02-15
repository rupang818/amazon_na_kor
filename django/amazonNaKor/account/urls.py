from django.urls import path
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('findus', views.findus, name='home'),
    path('login', LoginView.as_view(template_name='account/login.html'), name='login'),
    path('logout', LogoutView.as_view(template_name='account/logout.html'), name='logout'),
    path('register', views.register, name='register'),
    path('registerRecepient', views.registerRecepient, name='registerRecepient'),
    path('registerPackage', views.registerPackage, name='registerPackage'),
    path('registerItem', views.registerItem, name='registerItem'),
    path('registerDelivery', views.registerDelivery, name='registerDelivery'),
    path('profile', views.view_profile, name='view_profile'),
    path('profile/edit', views.edit_profile, name='edit_profile'),
    path('view_recepients', views.view_recepients, name='view_recepients'),
    path('view_packages', views.view_packages, name='view_packages'),
    path('view_items', views.view_items, name='view_items'),
    path('change-password', views.change_password, name='change_password'),
    path('reset-password', PasswordResetView.as_view(), name='reset-password'),
    path('reset-password/done', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password/complete', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('download-csv/', views.download_csv, name='download_csv'),
]