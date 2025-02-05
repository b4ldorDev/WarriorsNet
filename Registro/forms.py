from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class RobotRegistrationForm(forms.Form):
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

    def clean_correo_electronico(self):
        """Validación personalizada para el correo electrónico"""
        email = self.cleaned_data.get('correo_electronico')
        if email and not email.endswith('@tec.mx'):
            raise ValidationError('El correo electrónico debe ser institucional (@tec.mx)')
        return email

    def clean_name_robot(self):
        """Validación personalizada para el nombre del robot"""
        name = self.cleaned_data.get('name_robot')
        if name and len(name.strip()) < 3:
            raise ValidationError('El nombre del robot debe tener al menos 3 caracteres')
        return name.strip()

    def clean_matricula(self):
        """Validación personalizada para la matrícula"""
        matricula = self.cleaned_data.get('matricula')
        if matricula:
            if not matricula.startswith('A'):
                raise ValidationError('La matrícula debe comenzar con la letra A')
            if not matricula[1:].isdigit():
                raise ValidationError('Los últimos 8 caracteres deben ser números')
        return matricula