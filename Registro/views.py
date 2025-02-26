from django.shortcuts import render, HttpResponse, redirect , get_object_or_404
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User 
from .forms import RobotRegistrationForm
from .models import Usuario, Match, Torneo, Ronda, Robot
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test, login_required
from .forms import RobotRegistrationForm

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
                
                # Crear el robot asociado al usuario
                for categoria in categorias:
                    Robot.objects.create(
                        nombre=name_robot,
                        descripcion="Descripción del robot",  # Puedes ajustar la descripción según sea necesario
                        peso=0.0,  # Puedes ajustar el peso según sea necesario
                        categoria=categoria,
                        usuario=user,
                        fecha_registro=user.date_joined  # Usar la fecha de registro del usuario
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
        torneo = get_object_or_404(Torneo, id=torneo_id)
        torneo.generar_rondas()
        messages.success(request, 'Rondas generadas exitosamente')
        return redirect('panel_rondas')

    torneos = Torneo.objects.filter(esta_activo=True)
    return render(request, 'generar_rondas.html', {'torneos': torneos})

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def panel_rondas(request):
    rondas = Ronda.objects.all()
    return render(request, 'panel_rondas.html', {'rondas': rondas})

# Apartado para jurados y acceso a los torneos   
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