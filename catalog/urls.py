from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Equipment
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/list/', views.equipment_list, name='equipment_list'),
    path('equipment/<int:pk>/', views.equipment_detail, name='equipment_detail'),
    
    # Categories
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    
    # Projects
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    
    # Admin/Stats
    path('stats/', views.database_stats, name='database_stats'),
]
