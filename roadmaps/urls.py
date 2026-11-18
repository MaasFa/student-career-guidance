from django.urls import path
from . import views

urlpatterns = [
    path('', views.roadmap_list, name='roadmap_list'),
    path('<slug:slug>/', views.roadmap_detail, name='roadmap_detail'),
]