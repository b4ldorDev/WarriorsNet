from django.contrib import admin
from django.urls import path
from Registro  import views

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('', views.home, name='home'),
    path('home/', views.home, name='home'), 
    path('formulario/', views.formulario, name='formulario'), 
    path('login/', views.login_view, name='login'),
    path('about/', views.about, name='about'),        
    path('matches/', views.match_list, name='matches'),
  #  path('bracket/', views.bracket_list, name='matches'), 
    path('brackets/', views.brackets, name='brackets'),
    path('bracket/<int:torneo_id>/', views.ver_bracket, name='ver_bracket'),
    path('panel_jurado/', views.lista_torneos_jurado, name='lista_torneos_jurado'),
    path('torneo/<int:torneo_id>/jurado/', views.panel_jurado, name='panel_jurado'),

]
