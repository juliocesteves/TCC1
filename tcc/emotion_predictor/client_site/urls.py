from django.urls import path

from . import views

urlpatterns = [
    path('/index', views.index, name='index'),
    path('/index_json', views.index_json, name='index_json'),
]
