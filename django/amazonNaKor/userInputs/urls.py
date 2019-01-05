from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('thanks', views.thanks, name='thanks'),
    path('input', views.get_invoice, name='input'),
    path('login', LoginView.as_view(template_name='userInputs/login.html'), name='login'),
    path('logout', LogoutView.as_view(template_name='userInputs/logout.html'), name='logout'),
    path('register', views.register, name='register'),
]