from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('thanks', views.thanks, name='thanks'),
    path('input', views.get_invoice, name='input'),
    # path('output', views.get_invoice, name='output'),
]