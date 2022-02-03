from django.urls import path
from zoomcar.views import ComentarioUsuarioView, ComentarioView, LoginGoogleCheckView, ReservaIDView, ReservasTrayectosView, ReservasUsuarioView, ReservasView, UsuarioView, UsuarioIDView, VehiculoIDView, VehiculoView, TrayectoView, TrayectoIDView, VehiculosUsuarioView, TrayectosUsuarioView, GasolineraAPIView, TiempoView, IncidenciasTraficoAPIView, LoginGoogle

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
    path("incidenciasTrafico", IncidenciasTraficoAPIView.as_view()),
    path("oauth", LoginGoogle.as_view()),
    path("oauth/check", LoginGoogleCheckView.as_view()),
    path("usuarios/<int:id>/reservas", ReservasUsuarioView.as_view()),
    path("reservas", ReservasView.as_view()),
    path("reservas/<int:id>", ReservaIDView.as_view()),
    path("trayectos/<int:id>/reservas", ReservasTrayectosView.as_view()),
    path("usuarios/<int:id>/comentarios",ComentarioUsuarioView.as_view()),
    path("comentarios", ComentarioView.as_view())
]
