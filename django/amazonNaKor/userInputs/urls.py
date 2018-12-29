from django.urls import path
from django.conf.urls import url
from django.contrib.auth.views import login

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('thanks', views.thanks, name='thanks'),
    path('input', views.get_invoice, name='input'),
    url(r'^login/$'. login, {'template_name': 'userInputs/login.html'})
]