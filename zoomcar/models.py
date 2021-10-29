from django.db import models
from django.db.models.fields import CharField, EmailField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UsuarioManager(BaseUserManager):
    create_user()

# Create your models here.
class Usuario (AbstractBaseUser):
    email = EmailField(max_length=100, unique=True)
    name = CharField(max_length=50)
    surname = CharField(max_length=100)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

