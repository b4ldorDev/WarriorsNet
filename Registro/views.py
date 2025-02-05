from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User 
from django.http import HttpResponse
from . forms import RobotRegistrationForm
from . models import Usuario
from django.db import IntegrityError
from django.contrib import messages


def home(request):
    return render(request, 'home.html')

def formulario(request):
    """Vista para el formulario de registro de robots"""
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