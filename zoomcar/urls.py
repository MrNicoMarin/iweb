from django.urls import path
from zoomcar.views import UsuarioView, UsuarioIDView, VehiculoIDView, VehiculoView, TrayectoView, TrayectoIDView

urlpatterns = [
    path("usuario", UsuarioView.as_view()),
    path("usuario/<int:id>", UsuarioIDView.as_view()),
    path("vehiculo", VehiculoView.as_view()),
    path("vehiculo/<int:id>", VehiculoIDView.as_view()),
    path("trayecto", TrayectoView.as_view()),
    path("trayecto/<int:id>", TrayectoIDView.as_view())
]