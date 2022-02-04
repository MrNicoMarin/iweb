from django.db import models
from django.db.models.fields import CharField, DateField, EmailField, FloatField, IntegerField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import datetime

class UsuarioManager(BaseUserManager):
    def create_user(self, email, name, password):
        if not email:
            raise ValueError('Debe tener email')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password)

        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)

        return user

class Usuario (AbstractBaseUser, PermissionsMixin):
    email = EmailField(max_length=100, unique=True)
    name = CharField(max_length=50)
    apellidos = CharField(max_length=100, default=None)
    is_staff = models.BooleanField(default=False)
    imagen = models.CharField(max_length=100)
    fechaNacimiento = models.DateField()
    twitterToken = models.CharField(max_length=500, default=None)
    twitterTokenRefresh = models.CharField(max_length=500, default=None)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']


class Ubicacion (models.Model):
    latitud = FloatField()
    longitud = FloatField()
    municipio = CharField(max_length=50)

class Vehiculo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    modelo = CharField(max_length=50)
    color = CharField(max_length=20)
    matricula = CharField(max_length=10)
    imagen = CharField(max_length=100)
    plazas = IntegerField()

class Trayecto(models.Model):
    origen = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='origen')
    paradas = models.ManyToManyField(Ubicacion)
    destino = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='destino')
    piloto = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    precio = models.FloatField()
    fechaSalida = models.DateTimeField()

class Reserva(models.Model):
    trayecto = models.ForeignKey(Trayecto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fechaReserva = models.DateTimeField(default=datetime.now())

class Comentario(models.Model):
    creador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="creador")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="usuario")
    text = CharField(max_length=5000)
