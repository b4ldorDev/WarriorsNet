from django.contrib import admin
from .models import Usuario, Robot, Torneo, Ronda, Match, Notificacion

admin.site.register(Usuario)
admin.site.register(Robot)
admin.site.register(Torneo)
admin.site.register(Ronda)
admin.site.register(Match)
admin.site.register(Notificacion)