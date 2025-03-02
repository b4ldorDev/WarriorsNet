from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User 
from .forms import RobotRegistrationForm
from .models import Usuario, Match, Torneo, Ronda, Robot, actualizar_bracket
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test, login_required
from .forms import RobotRegistrationForm
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'home.html')

def torneo(request): 
    return render(request, 'torneo.html')

def ver_bracket(request, torneo_id):
    torneo = get_object_or_404(Torneo, id=torneo_id)
    
    #filtro para las categorias 
    rondas_profesional = torneo.rondas.filter(categoria='PROFESIONAL').prefetch_related(
        'matches__robot1',
        'matches__robot2',
        'matches__ganador'
    ).order_by('numero_ronda')
    
    rondas_junior = torneo.rondas.filter(categoria='JUNIOR').prefetch_related(
        'matches__robot1',
        'matches__robot2',
        'matches__ganador'
    ).order_by('numero_ronda')
    
    context = {
        'torneo': torneo,
        'rondas_profesional': rondas_profesional,
        'rondas_junior': rondas_junior,
    }
    return render(request, 'torneos/bracket.html', context)

def match_list(request):
    search_query = request.GET.get('name_robot', '')

    if search_query: 
        matches = Match.objects.filter(            
            Q(robot1__nombre__icontains=search_query) | 
            Q(robot2__nombre__icontains=search_query)
        ).order_by('hora_programada')
    else: 
        matches = Match.objects.all().order_by('hora_programada')

    context = {
        'matches': matches,
        'search_query': search_query  
    }

    return render(request, 'torneos/match_list.html', context)

def formulario(request):
    if request.method == 'GET':
        form = RobotRegistrationForm()
        return render(request, 'formulario.html', {'form': form})
    
    elif request.method == 'POST':
        form = RobotRegistrationForm(request.POST, request.FILES)
        
        if not form.is_valid():
            messages.error(request, 'Por favor, verifica los datos ingresados.')
            return render(request, 'formulario.html', {'form': form})
            
        correo = form.cleaned_data['correo_electronico']
        name_robot = form.cleaned_data['name_robot']
        categorias = form.cleaned_data['categorias']
        comprobante_pago = form.cleaned_data['comprobante_pago']
        matricula = form.cleaned_data['matricula'] if form.cleaned_data['matricula'] else form.cleaned_data['correo_electronico']
    
        try:
            with transaction.atomic():
                # Crear el usuario
                user = Usuario.objects.create_user(
                    username=matricula,
                    name_robot=name_robot,
                    correo_electronico=correo,
                    is_tec_student=form.cleaned_data['is_tec_student']
                )
                
                # Crear el robot asociado al usuario para cada categoría
                for categoria in categorias:
                    Robot.objects.create(
                        nombre=name_robot,
                        descripcion="Descripción del robot",
                        peso=0.0,
                        categoria=categoria,
                        usuario=user,
                        fecha_registro=user.date_joined
                    )
                
                # Guardar el comprobante de pago si se proporciona
                if comprobante_pago:
                    user.comprobante_pago = comprobante_pago
                    user.save()
                
                messages.success(request, 'Usuario y Robot registrados exitosamente')
                return redirect('home') 
                
        except IntegrityError:
            messages.error(request, 'Esta matrícula o correo ya están registrados')
            return render(request, 'formulario.html', {'form': form})
            
        except Exception as e:
            messages.error(request, f'Error al registrar: {str(e)}')
            return render(request, 'formulario.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def generar_rondas(request):
    if request.method == 'POST':
        torneo_id = request.POST.get('torneo_id')
        logger.info(f"Intentando generar rondas para torneo ID: {torneo_id}")
        
        try:
            torneo = get_object_or_404(Torneo, id=torneo_id)
            logger.info(f"Torneo encontrado: {torneo.nombre}")
            
            # Contar robots por categoría
            robots_profesional = Robot.objects.filter(categoria='PROFESIONAL').count()
            robots_junior = Robot.objects.filter(categoria='JUNIOR').count()
            
            logger.info(f"Robots profesionales: {robots_profesional}, Robots junior: {robots_junior}")
            
            if robots_profesional < 2 and robots_junior < 2:
                logger.warning("No hay suficientes robots para generar rondas")
                messages.warning(request, 'No hay suficientes robots inscritos en ninguna categoría para generar rondas.')
            else:
                logger.info("Iniciando generación de rondas")
                torneo.generar_rondas()
                logger.info("Rondas generadas correctamente")
                messages.success(request, 'Rondas generadas con éxito.')
        except Exception as e:
            logger.error(f"Error al generar rondas: {str(e)}", exc_info=True)
            messages.error(request, f'Error al generar rondas: {str(e)}')
    
    return redirect('admin_torneos')

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def panel_rondas(request):
    rondas = Ronda.objects.all().select_related('torneo')
    
    context = {
        'rondas': rondas,
        'titulo': 'Panel de Administración de Rondas'
    }
    
    return render(request, 'torneos/panel_rondas.html', context)

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

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_torneos(request):
    torneos = Torneo.objects.all().order_by('-fecha_inicio')
    context = {
        'torneos': torneos,
        'titulo': 'Administración de Torneos'
    }
    return render(request, 'torneos/admin_torneos.html', context)