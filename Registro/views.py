from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm 
from . forms import FormularioSimple 


def home(request):
    return render(request, 'home.html')

def formulario(request):
    if request.method =='POST':
        form  = FormularioSimple(request.POST)
        if form.is_valid():
            form.save()
    else: 
        form = FormularioSimple()
    return render(request, 'formulario.html', {'form': form})