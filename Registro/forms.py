from django import forms 
from . models import Usuario 

class FormularioSimple(forms.ModelForm): 
    class Meta: 
        model = Usuario
        fields = [
            'matricula',  
            'correo_electronico',
            'numero_telefono',
        ]
