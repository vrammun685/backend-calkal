# Generated by Django 5.1.3 on 2025-06-11 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kal_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pesoregistrado',
            name='foto_pesaje',
            field=models.ImageField(blank=True, null=True, upload_to='usuarios/pesajes/'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='imagen_Perfil',
            field=models.ImageField(blank=True, null=True, upload_to='usuarios/perfiles/'),
        ),
    ]
