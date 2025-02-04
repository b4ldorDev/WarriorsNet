from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    matricula = models.CharField(max_length=255)
    correo_electronico = models.EmailField(unique=True)
    numero_telefono = models.CharField(max_length=15, unique=True)
    es_administrador = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return self.correo_electronico
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='registro_users',  
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='registro_users_permissions',  
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )

class Robot(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    peso = models.FloatField()
    categoria = models.CharField(max_length=50)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='robots')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.categoria})"

    class Meta:
        ordering = ['-fecha_registro']

class Torneo(models.Model):
    nombre = models.CharField(max_length=200)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    ubicacion = models.CharField(max_length=255)
    descripcion = models.TextField()
    esta_activo = models.BooleanField(default=True)
    administrador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='torneos_administrados')

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['-fecha_inicio']

class Ronda(models.Model):
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name='rondas')
    numero_ronda = models.IntegerField()
    hora_inicio = models.DateTimeField()
    hora_fin = models.DateTimeField()
    esta_completa = models.BooleanField(default=False)

    def __str__(self):
        return f"Ronda {self.numero_ronda} - {self.torneo.nombre}"

    class Meta:
        ordering = ['numero_ronda']
        unique_together = ['torneo', 'numero_ronda']

class Match(models.Model):
    ronda = models.ForeignKey(Ronda, on_delete=models.CASCADE, related_name='matches')
    robot1 = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='matches_como_robot1')
    robot2 = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='matches_como_robot2')
    ganador = models.ForeignKey(Robot, on_delete=models.SET_NULL, null=True, related_name='matches_ganados')
    hora_programada = models.DateTimeField()
    esta_completo = models.BooleanField(default=False)
    descripcion_resultado = models.TextField(blank=True)

    def __str__(self):
        return f"{self.robot1.nombre} vs {self.robot2.nombre}"

    class Meta:
        verbose_name_plural = 'matches'
        ordering = ['hora_programada']

class Notificacion(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    programada_para = models.DateTimeField()
    esta_enviada = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Notificación para {self.match}"

    def enviar(self):
        self.esta_enviada = True
        self.fecha_envio = timezone.now()
        self.save()

    class Meta:
        ordering = ['programada_para']