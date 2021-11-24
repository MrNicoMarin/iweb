from django.contrib import admin
from zoomcar.models import Reserva, Trayecto, Ubicacion, Usuario, Vehiculo

# Register your models here.

admin.site.register(Usuario)
admin.site.register(Ubicacion)
admin.site.register(Trayecto)
admin.site.register(Vehiculo)
admin.site.register(Reserva)