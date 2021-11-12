from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from zoomcar.dto import UsuarioDto, UbicacionDto
from zoomcar.serializers import UsuarioSerializer, UbicacionSerializer
from zoomcar.models import Usuario, Ubicacion


from zoomcar.models import Usuario, Ubicacion
# Create your views here.

class UsuarioView(APIView):
    def get(self, request, format=None):
        users = Usuario.objects.all()

        usersDTO = UsuarioDto.toUsuariosDto(users)
        serializer = UsuarioSerializer(usersDTO, many=True)
        
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = Usuario(name=serializer.validated_data.get('name'),
            email=serializer.validated_data.get('email'))
            usuario.set_password(serializer.validated_data.get('password'))
            usuario.save()
        
        return Response()

class UsuarioIDView(APIView):
    def get(self, request, id, format=None):
        user = Usuario.objects.get(id=id)

        userDTO = UsuarioDto(user)
        serializer = UsuarioSerializer(userDTO)
        
        return Response(serializer.data)    

class UbicacionView(APIView):
    def get(self,request,format=None):
        ubicaciones = Ubicacion.objects.all()
        
        ubicacionesDto = UbicacionDto.toUbicacionDto(ubicaciones)
        serializer = UbicacionSerializer(ubicacionesDto, many=True)
        
        return Response(serializer.data)

    def post(self,request,format=None):
        serializer = UbicacionSerializer(data=request.data)
        if serializer.is_valid():
            ubicacion = Ubicacion(longitud=serializer.validated_data.get('longitud'),
            latitud=serializer.validated_data.get('latitud'))
            ubicacion.save()
        
        return Response()

    
