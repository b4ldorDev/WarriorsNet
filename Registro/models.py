from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import transaction
import random

class Usuario(AbstractUser):
    name_robot = models.CharField(max_length=100)
    matricula = models.CharField(max_length=9, null=True, blank=True)
    correo_electronico = models.EmailField(unique=True)
    is_tec_student = models.BooleanField(default=False)
    profesional = models.BooleanField(default=False)
    junior = models.BooleanField(default=False)
#No sé luego lo hago chido 

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

    def generar_rondas(self):
        """Genera las rondas y matches del torneo automáticamente."""
        robots = list(Robot.objects.filter(
            matches_como_robot1__ronda__torneo=self
        ).distinct())
        
        if len(robots) < 2:
            raise ValueError("Se necesitan al menos 2 robots para generar las rondas")

        with transaction.atomic():
            self.rondas.all().delete()
            
            num_robots = len(robots)
            num_rondas = (num_robots - 1).bit_length()
            
            primera_ronda = Ronda.objects.create(
                torneo=self,
                numero_ronda=1,
                hora_inicio=self.fecha_inicio,
                hora_fin=self.fecha_inicio + timezone.timedelta(hours=2)
            )
            
            random.shuffle(robots)
            
            matches_primera_ronda = []
            for i in range(0, len(robots), 2):
                if i + 1 < len(robots):
                    match = Match.objects.create(
                        ronda=primera_ronda,
                        robot1=robots[i],
                        robot2=robots[i + 1],
                        hora_programada=self.fecha_inicio + timezone.timedelta(minutes=30 * (i // 2))
                    )
                    matches_primera_ronda.append(match)
                else:
                    match = Match.objects.create(
                        ronda=primera_ronda,
                        robot1=robots[i],
                        robot2=None,
                        ganador=robots[i],
                        esta_completo=True,
                        hora_programada=self.fecha_inicio + timezone.timedelta(minutes=30 * (i // 2))
                    )
                    matches_primera_ronda.append(match)
            
            for num_ronda in range(2, num_rondas + 1):
                nueva_ronda = Ronda.objects.create(
                    torneo=self,
                    numero_ronda=num_ronda,
                    hora_inicio=self.fecha_inicio + timezone.timedelta(days=num_ronda-1),
                    hora_fin=self.fecha_inicio + timezone.timedelta(days=num_ronda-1, hours=2)
                )
                
                num_matches = len(matches_primera_ronda) // 2
                for i in range(num_matches):
                    Match.objects.create(
                        ronda=nueva_ronda,
                        robot1=None,
                        robot2=None,
                        hora_programada=nueva_ronda.hora_inicio + timezone.timedelta(minutes=30 * i)
                    )

def actualizar_bracket(match):
    if not match.esta_completo or not match.ganador:
        return
        
    ronda_actual = match.ronda
    siguiente_ronda = Ronda.objects.filter(
        torneo=ronda_actual.torneo,
        numero_ronda=ronda_actual.numero_ronda + 1
    ).first()
    
    if siguiente_ronda:
        matches_actuales = list(match.ronda.matches.order_by('id'))
        indice_actual = matches_actuales.index(match)
        siguiente_indice = indice_actual // 2
        
        siguiente_match = siguiente_ronda.matches.all().order_by('id')[siguiente_indice]
        
        if indice_actual % 2 == 0:
            siguiente_match.robot1 = match.ganador
        else:
            siguiente_match.robot2 = match.ganador
        
        siguiente_match.save()


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

def ver_bracket(request, torneo_id):
    torneo = Torneo.objects.get(id=torneo_id)
    rondas = torneo.rondas.all().prefetch_related('matches')
    context = {'torneo': torneo, 'rondas': rondas}
    return render(request, 'torneos/bracket.html', context)


