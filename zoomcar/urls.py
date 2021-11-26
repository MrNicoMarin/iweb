from django.urls import path
from zoomcar.views import UsuarioView, UsuarioIDView, VehiculoIDView, VehiculoView, TrayectoView, TrayectoIDView, VehiculosUsuarioView, TrayectosUsuarioView, GasolineraAPIView, TiempoView, IncidenciasTraficoAPIView

urlpatterns = [
    path("usuarios", UsuarioView.as_view()),
    path("usuarios/<int:id>", UsuarioIDView.as_view()),
    path("vehiculos", VehiculoView.as_view()),
    path("vehiculos/<int:id>", VehiculoIDView.as_view()),
    path("trayectos", TrayectoView.as_view()),
    path("trayectos/<int:id>", TrayectoIDView.as_view()),
    path("usuarios/<int:id>/vehiculos", VehiculosUsuarioView.as_view()),
    path("usuarios/<int:id>/trayectos", TrayectosUsuarioView.as_view()),
    path("gasolineras", GasolineraAPIView.as_view()),
    path("predicciones", TiempoView.as_view()),
    path("incidenciasTrafico", IncidenciasTraficoAPIView.as_view())
]
