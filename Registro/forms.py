from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import Usuario 
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

class RobotRegistrationForm(forms.Form):
    is_tec_student = forms.BooleanField(
        required=False,
        label='Soy estudiante del ITESM',
        widget=forms.CheckboxInput(attrs={'class' : 'form-check-input'})
    )    
    matricula = forms.CharField(
        label='Matrícula / Usuario(externos)',
        max_length=9,
        min_length=9,
        required=False,
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
            'placeholder': 'ejemplo@tec.mx /ejemplo@gmail.com '
        })
    )
    
    categorias_choices = [('PROFESIONAL', 'Profesional'), ('JUNIOR', 'Junior')]
    categorias = forms.MultipleChoiceField(
        label='Categorías',
        choices=categorias_choices,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    comprobante_pago = forms.ImageField(
        label='Comprobante de Pago (máximo 2 MB)',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    )

    def clean_comprobante_pago(self):
        imagen = self.cleaned_data.get('comprobante_pago')
        if imagen and imagen.size > 2 * 1024 * 1024:
            raise ValidationError('El tamaño del archivo no debe superar los 2 MB.')
        return imagen
        
    def clean_categorias(self):
        categorias = self.cleaned_data.get('categorias')
        if not categorias:
            raise ValidationError('Debe seleccionar al menos una categoría.')
        return categorias

    def clean_name_robot(self):
        name = self.cleaned_data.get('name_robot')
        if name and len(name.strip()) < 3:
            raise ValidationError('El nombre del robot debe tener al menos 3 caracteres')
        return name.strip()

    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula')
        is_tec_student = self.cleaned_data.get('is_tec_student')
        if is_tec_student:
            if not matricula.startswith('A'):
                raise ValidationError('La matrícula debe comenzar con la letra A')
            if not matricula[1:].isdigit():
                raise ValidationError('Los últimos 8 caracteres deben ser números')
        return matricula
    
    def clean_correo_electronico(self):
        email = self.cleaned_data.get('correo_electronico')
        is_tec_student = self.cleaned_data.get('is_tec_student')
        if is_tec_student and not email.endswith('@tec.mx'):
            raise ValidationError('El correo electrónico debe ser institucional (@tec.mx)')
        return email

    def Meta(self):
        model = Usuario
        fields = ['name_robot', 'matricula', 'correo_electronico', 'is_tec_student', 'comprobante_pago']
    
    def clean(self):
        cleaned_data = super().clean()
        is_tec_student = cleaned_data.get('is_tec_student')
        matricula = cleaned_data.get('matricula')
        if is_tec_student and not matricula: 
            raise ValidationError('La matrícula es obligatoria para estudiantes del ITESM')
        return cleaned_data