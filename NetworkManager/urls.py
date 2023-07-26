from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('devices',views.devices),
    path('configuration',views.configuration)
]