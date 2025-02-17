from .models import Robot
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import Usuario 


class RobotRegistrationForm(forms.Form):
    is_tec_student = forms.BooleanField(
        required=False,
        label='Soy estudiante del ITESM',
        widget=forms.CheckboxInput(attrs={'class' : 'form-check-input'})
    )    
    matricula = forms.CharField(
        label='Matrícula',
        max_length=9,
        min_length=9,
        validators=[
            RegexValidator(
                regex='^[A-Z0-9]*$',
                message='La matrícula solo debe contener letras mayúsculas y números'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ejemplo: A01234567'
        })
    )

    name_robot = forms.CharField(
        label='Nombre del Robot',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de tu robot'
        })
    )

    correo_electronico = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@tec.mx'
        })
    )


    def clean_name_robot(self):
        name = self.cleaned_data.get('name_robot')
        if name and len(name.strip()) < 3:
            raise ValidationError('El nombre del robot debe tener al menos 3 caracteres')
        return name.strip()


    def Meta(self):
        model = Usuario
        fields = ['name_robot', 'matricula', 'correo_electronico', 'is_tec_student']
    
    
    def clean(self):
        clean_data = super().clean()
        is_tec_student = cleaned_data.get('is_tec_student')
        matricula = cleaned_data.get('matricula')
        if is_tec_student and not matricula: 
            raise forms.ValidationError(
                "Favor de escribir la matricula para alumnos del Tec"
            )
            
        if not is_tec_student:
            cleaned_data['matricula']= None
        return cleaned_data

class JuradoMatchForm(forms.Form):
    ganador = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect,
        empty_label=None
    )
    descripcion_resultado = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )

    def __init__(self, match, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(match.robot1.id, match.robot1.nombre)]
        if match.robot2:
            choices.append((match.robot2.id, match.robot2.nombre))
        self.fields['ganador'].queryset = Robot.objects.filter(id__in=[c[0] for c in choices])


"""
    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula')
        if matricula:
            if not matricula.startswith('A'):
                raise ValidationError('La matrícula debe comenzar con la letra A')
            if not matricula[1:].isdigit():
                raise ValidationError('Los últimos 8 caracteres deben ser números')
        return matricula
        
    def clean_correo_electronico(self):
        email = self.cleaned_data.get('correo_electronico')
        if email and not email.endswith('@'):
            raise ValidationError('El correo electrónico debe ser institucional (@tec.mx)')
        return email
"""