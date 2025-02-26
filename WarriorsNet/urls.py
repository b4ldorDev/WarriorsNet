"""
URL configuration for WarriorsNet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Registro  import views

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('', views.home, name='home'),
    path('home/', views.home, name='home'), 
    path('formulario/', views.formulario, name='formulario'), 
    path('torneo/', views.torneo, name='torneo'),  
    path('matches/', views.match_list, name='matches'),  
    path('bracket/<int:torneo_id>/', views.ver_bracket, name='ver_bracket'),    
    path('generar_rondas/', views.generar_rondas, name='generar_rondas'),
    path('panel_rondas/', views.panel_rondas, name='panel_rondas'),
    path('lista_torneos_jurado/', views.lista_torneos_jurado, name='lista_torneos_jurado'),    
]
