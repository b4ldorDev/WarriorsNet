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
    comprobante_pago = models.ImageField(upload_to='comprobantes/', null=True, blank=True)
    pago_verificado = models.BooleanField(default=False)
    # No sé luego lo hago chido 

class Robot(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    peso = models.FloatField()
    categoria = models.CharField(max_length=50)  # 'PROFESIONAL' o 'JUNIOR'
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
    # Agregamos relación para inscribir robots directamente a un torneo
    robots_inscritos = models.ManyToManyField(Robot, related_name='torneos', blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['-fecha_inicio']

    def generar_rondas(self):

        robots_profesional = list(self.robots_inscritos.filter(categoria='PROFESIONAL'))
        robots_junior = list(self.robots_inscritos.filter(categoria='JUNIOR'))
        
        self.rondas.all().delete()

        for categoria, robots in [('PROFESIONAL', robots_profesional), ('JUNIOR', robots_junior)]:
            if len(robots) < 2:
                continue  
                
            self._crear_rondas_para_categoria(robots, categoria)

    def _crear_rondas_para_categoria(self, robots, categoria):
        with transaction.atomic():
            num_robots = len(robots)
            num_rondas = (num_robots - 1).bit_length()  # Calcula cuántas rondas necesitamos
            
            primera_ronda = Ronda.objects.create(
                torneo=self,
                numero_ronda=1,
                hora_inicio=self.fecha_inicio,
                hora_fin=self.fecha_inicio + timezone.timedelta(hours=2)
            )
            
            random.shuffle(robots)  # Mezclamos los robots para emparejarlos al azar
            
            matches_primera_ronda = []
            # Crear matches para la primera ronda
            for i in range(0, num_robots, 2):
                if i + 1 < num_robots:  # Tenemos un par de robots
                    match = Match.objects.create(
                        ronda=primera_ronda,
                        robot1=robots[i],
                        robot2=robots[i + 1],
                        hora_programada=self.fecha_inicio + timezone.timedelta(minutes=30 * (i // 2))
                    )
                else:  # Un robot sin pareja, pasa automáticamente
                    match = Match.objects.create(
                        ronda=primera_ronda,
                        robot1=robots[i],
                        robot2=None,  # Sin rival
                        ganador=robots[i],  # Gana automáticamente
                        esta_completo=True,
                        hora_programada=self.fecha_inicio + timezone.timedelta(minutes=30 * (i // 2))
                    )
                matches_primera_ronda.append(match)
            
            # Crear las siguientes rondas (inicialmente vacías)
            for num_ronda in range(2, num_rondas + 1):
                nueva_ronda = Ronda.objects.create(
                    torneo=self,
                    numero_ronda=num_ronda,
                    hora_inicio=self.fecha_inicio + timezone.timedelta(days=num_ronda-1),
                    hora_fin=self.fecha_inicio + timezone.timedelta(days=num_ronda-1, hours=2)
                )
                
                num_matches = 2 ** (num_rondas - num_ronda)  # Número de matches en esta ronda
                for i in range(num_matches):
                    Match.objects.create(
                        ronda=nueva_ronda,
                        robot1=None,  # Se llenará después
                        robot2=None,  # Se llenará después
                        hora_programada=nueva_ronda.hora_inicio + timezone.timedelta(minutes=30 * i)
                    )

class Ronda(models.Model):
    CATEGORIA_CHOICES = [
        ('PROFESIONAL', 'Profesional'),
        ('JUNIOR', 'Junior'),
    ]
    
    torneo = models.ForeignKey(Torneo, related_name='rondas', on_delete=models.CASCADE)
    numero_ronda = models.IntegerField()
    esta_completa = models.BooleanField(default=False)
    hora_inicio = models.DateTimeField(null=True, blank=True)
    hora_fin = models.DateTimeField(null=True, blank=True)
    lugar = models.CharField(max_length=100, blank=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='PROFESIONAL')
    
    class Meta:
        unique_together = ('torneo', 'numero_ronda', 'categoria')
        
    def __str__(self):
        return f"Ronda {self.numero_ronda} - {self.torneo.nombre} - {self.get_categoria_display()}"

class Match(models.Model):
    ronda = models.ForeignKey(Ronda, on_delete=models.CASCADE, related_name='matches')
    robot1 = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='matches_como_robot1', null=True)
    robot2 = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='matches_como_robot2', null=True)
    ganador = models.ForeignKey(Robot, on_delete=models.SET_NULL, null=True, related_name='matches_ganados')
    hora_programada = models.DateTimeField()
    esta_completo = models.BooleanField(default=False)
    descripcion_resultado = models.TextField(blank=True)

    def __str__(self):
        robot1_nombre = self.robot1.nombre if self.robot1 else "TBD"
        robot2_nombre = self.robot2.nombre if self.robot2 else "TBD"
        return f"{robot1_nombre} vs {robot2_nombre}"

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

def actualizar_bracket(match):
    """
    Actualiza el bracket después de que un match ha sido completado.
    Mueve al ganador a la siguiente ronda.
    """
    if not match.esta_completo or not match.ganador:
        return
        
    ronda_actual = match.ronda
    siguiente_ronda = Ronda.objects.filter(
        torneo=ronda_actual.torneo,
        categoria=ronda_actual.categoria,  # Asegura que sea la misma categoría
        numero_ronda=ronda_actual.numero_ronda + 1
    ).first()
    
    if siguiente_ronda:
        matches_actuales = list(match.ronda.matches.order_by('id'))
        indice_actual = matches_actuales.index(match)
        siguiente_indice = indice_actual // 2
        
        siguientes_matches = list(siguiente_ronda.matches.order_by('id'))
        if siguiente_indice < len(siguientes_matches):
            siguiente_match = siguientes_matches[siguiente_indice]
            
            # Determinar si el ganador va como robot1 o robot2
            if indice_actual % 2 == 0:
                siguiente_match.robot1 = match.ganador
            else:
                siguiente_match.robot2 = match.ganador
            
            siguiente_match.save()