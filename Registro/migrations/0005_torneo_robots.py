# Generated by Django 5.1.5 on 2025-03-01 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Registro', '0004_alter_ronda_lugar'),
    ]

    operations = [
        migrations.AddField(
            model_name='torneo',
            name='robots',
            field=models.ManyToManyField(blank=True, related_name='torneos', to='Registro.robot'),
        ),
    ]
