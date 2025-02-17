from django.shortcuts import render, HttpResponse, get_object_or_404, redirect 
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User 
from django.db import IntegrityError
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db import transaction
from django.contrib.auth import login, authenticate
from . forms import RobotRegistrationForm, JuradoMatchForm
from . models import Usuario, Match, Torneo, Ronda, Robot
from django.shortcuts import render, redirect, get_object_or_404

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirigir a diferentes páginas según el tipo de usuario
            if user.groups.filter(name='Jurados').exists():
                return redirect('lista_torneos_jurado')
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'login.html')

@login_required
def lista_torneos_jurado(request):
    if not request.user.groups.filter(name='Jurados').exists():
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('home')
        
    torneos = Torneo.objects.filter(esta_activo=True).order_by('-fecha_inicio')
    return render(request, 'torneos/lista_torneos_jurado.html', {
        'torneos': torneos,
        'titulo': 'Panel de Jurado - Torneos Activos'
    })

@login_required
def ver_bracket(request, torneo_id):
    torneo = get_object_or_404(Torneo, id=torneo_id)
    rondas = torneo.rondas.all().prefetch_related(
        'matches__robot1',
        'matches__robot2',
        'matches__ganador'
    ).order_by('numero_ronda')
    
    return render(request, 'torneos/bracket.html', {
        'torneo': torneo,
        'rondas': rondas,
    })


def iniciar_torneo(request, torneo_id):
    torneo = get_object_or_404(Torneo, id=torneo_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                torneo.generar_rondas()
                messages.success(request, 'Torneo iniciado exitosamente!')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al iniciar el torneo: {str(e)}')
        
    return redirect('tournament_dashboard')


def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')



def brackets(request):
    torneos = Torneo.objects.filter(esta_activo=True)
    return render(request, 'torneos/lista_brackets.html', {
        'torneos': torneos
    })
    
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

    return render(request, 'match_list.html', context)

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
      
    #APartado para jurados y acceso a los torneos   
def es_jurado(user):
    return user.groups.filter(name='Jurados').exists()

@user_passes_test(es_jurado)
def lista_torneos_jurado(request):
    """Vista para mostrar la lista de torneos disponibles para jurados."""
    torneos = Torneo.objects.filter(esta_activo=True).order_by('-fecha_inicio')
    
    return render(request, 'torneos/lista_torneos_jurado.html', {
        'torneos': torneos,
        'titulo': 'Panel de Jurado - Torneos Activos'
    })

@user_passes_test(es_jurado)
def panel_jurado(request, torneo_id):
    torneo = get_object_or_404(Torneo, id=torneo_id)
    ronda_actual = torneo.rondas.filter(esta_completa=False).order_by('numero_ronda').first()
    
    if not ronda_actual:
        messages.info(request, "Todas las rondas han sido completadas.")
        return redirect('ver_bracket', torneo_id=torneo_id)
    
    matches_pendientes = ronda_actual.matches.filter(
        esta_completo=False
    ).select_related('robot1', 'robot2')
    
    context = {
        'torneo': torneo,
        'ronda_actual': ronda_actual,
        'matches_pendientes': matches_pendientes,
    }
    
    return render(request, 'torneos/panel_jurado.html', context)
