from django.urls import path
from zoomcar.views import UsuarioView, UbicacionView, UsuarioIDView

urlpatterns = [
    path("usuario", UsuarioView.as_view()),
    path("usuario/<int:id>", UsuarioIDView.as_view()),
    path("ubicacion", UbicacionView.as_view())
]