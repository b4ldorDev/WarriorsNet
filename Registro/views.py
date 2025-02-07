from django.shortcuts import render, HttpResponse, redirect 
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User 
from . forms import RobotRegistrationForm
from . models import Usuario, Match, Torneo, Ronda
from django.db import IntegrityError
from django.contrib import messages
from django.db.models import Q

def home(request):
    return render(request, 'home.html')

def torneo(request): 
    return render(request, 'torneo.html')

def ver_bracket(request, torneo_id):
    torneo = Torneo.objects.get(id=torneo_id)
    rondas = torneo.rondas.all().prefetch_related('matches')
    
    context = {
        'torneo': torneo,
        'rondas': rondas,
    }
    return render(request, 'torneos/bracket.html', context)

def match_list(request):
    search_query = request.GET.get('name_robot', '')

    if search_query: 
        matches = Match.objects.filter(            
            Q(robot1__name__icontains=search_query) | 
            Q(robot2__name__icontains=search_query)
        ).order_by('hora_programada ')
    else: 
        matches = Match.objects.all().order_by('hora_programada')

    context = {
        'matches' : matches,
        'search_query': search_query  
    }

    return render(request, 'torneos/match_list.html', context)

def formulario(request):
    if request.method == 'GET':
        form = RobotRegistrationForm()
        return render(request, 'formulario.html', {'form': form})
    
    elif request.method == 'POST':
        form = RobotRegistrationForm(request.POST)
        
        if not form.is_valid():
            messages.error(request, 'Por favor, verifica los datos ingresados.')
            return render(request, 'formulario.html', {'form': form})
            
        correo = form.cleaned_data['correo_electronico']
        
        if not correo.endswith('@tec.mx'):
            messages.error(request, 'El correo debe ser institucional (@tec.mx)')
            return render(request, 'formulario.html', {'form': form})
            
        try:
            user = Usuario.objects.create_user(
                username=form.cleaned_data['matricula'],
                name_robot=form.cleaned_data['name_robot'],
                correo_electronico=correo
            )
            messages.success(request, 'Robot registrado exitosamente')
            return redirect('home') 
            
        except IntegrityError:
            messages.error(request, 'Esta matrícula o correo ya están registrados')
            return render(request, 'formulario.html', {'form': form})
            
        except Exception as e:
            messages.error(request, f'Error al registrar: {str(e)}')
            return render(request, 'formulario.html', {'form': form})