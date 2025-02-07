from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import transaction

class Usuario(AbstractUser):
    name_robot = models.CharField(max_length=50)
    correo_electronico  = models.EmailField(unique=True)

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

    def generar_rondas(self, robots):

        self.rondas.all().delete()
    
        num_rondas = len(robots).bit_length() - 1
    
        with transaction.atomic():
            for n_ronda in range(1, num_rondas + 1):
                ronda = Ronda.objects.create(
                    torneo=self,
                    numero_ronda=n_ronda,
                    hora_inicio=timezone.now(),
                    hora_fin=timezone.now(),
                )
            
                if n_ronda == 1:
                    robots_mezclados = list(robots)
                    random.shuffle(robots_mezclados)
                
                    for i in range(0, len(robots_mezclados), 2):
                        robot1 = robots_mezclados[i]
                        robot2 = robots_mezclados[i+1] if i+1 < len(robots_mezclados) else None
                    
                        Match.objects.create(
                            ronda=ronda,
                            robot1=robot1,
                            robot2=robot2,
                            hora_programada=timezone.now(),
                        )


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

#Funciones 

# Con esto muestro el diagrama ese de los batallas 
def ver_bracket(request, torneo_id):
    torneo = Torneo.objects.get(id=torneo_id)
    rondas = torneo.rondas.all().prefetch_related('matches')
    context = {'torneo': torneo, 'rondas': rondas}
    return render(request, 'torneos/bracket.html', context)


