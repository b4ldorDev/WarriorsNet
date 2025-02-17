from django.contrib.auth.models import Group

def setup_grupos():
    grupos_necesarios = ['Jurados', 'Participantes', 'Organizadores']
    for nombre_grupo in grupos_necesarios:
        Group.objects.get_or_create(name=nombre_grupo)

def asignar_jurado(usuario):
    grupo_jurados, _ = Group.objects.get_or_create(name='Jurados')
    usuario.groups.add(grupo_jurados)

def remover_jurado(usuario):
    grupo_jurados = Group.objects.get(name='Jurados')
    usuario.groups.remove(grupo_jurados)