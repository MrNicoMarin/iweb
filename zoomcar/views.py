from django.db.models import deletion
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from zoomcar.dto import UsuarioDto, UbicacionDto
from zoomcar.serializers import UsuarioSerializer, UbicacionSerializer
from zoomcar.models import Usuario, Ubicacion


from zoomcar.models import Usuario, Ubicacion

class UsuarioView(APIView):
    def get(self, request, format=None):
        users = Usuario.objects.all()

        usersDTO = UsuarioDto.toUsuariosDto(users)
        serializer = UsuarioSerializer(usersDTO, many=True)
        
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = Usuario(name=serializer.validated_data.get('name'),
            email=serializer.validated_data.get('email'),
            apellidos=serializer.validated_data.get('apellidos'))
            usuario.set_password(serializer.validated_data.get('password'))
            usuario.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_201_CREATED)

class UsuarioIDView(APIView):
    def get(self, request, id, format=None):
        user = Usuario.objects.get(id=id)

        userDTO = UsuarioDto(user)
        serializer = UsuarioSerializer(userDTO)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id, format=None):
        user = Usuario.objects.get(id=id)
        user.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

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

    
