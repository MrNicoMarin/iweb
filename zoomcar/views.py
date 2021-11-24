from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from zoomcar.dto import UsuarioDto, VehiculoDto, TrayectoDto, UbicacionDto
from zoomcar.serializers import UsuarioSerializer, VehiculoSerializer, TrayectoSerializer, UbicacionSerializer
from zoomcar.models import Usuario, Vehiculo, Trayecto, Ubicacion
from datetime import date, datetime
#import requests

class UsuarioView(APIView):
    def get(self, request, format=None):
        users = Usuario.objects.all()

        if (request.query_params.get('name') is not None):
            users = users.filter(name__icontains=request.query_params.get('name'))
        if (request.query_params.get('apellidos') is not None):
            users = users.filter(apellidos__icontains=request.query_params.get('apellidos'))


        if(request.query_params.get('edadMin') is not None):
            anioMinimo = int(datetime.today().strftime('%Y')) - int(request.query_params.get('edadMin'))
            fechaNacimientoMin = datetime.today().replace(day=31,month=12,year=anioMinimo)
            users = users.filter(fechaNacimiento__lte= fechaNacimientoMin)

        if(request.query_params.get('edadMax') is not None):
            anioMaximo = int(datetime.today().strftime('%Y')) - int(request.query_params.get('edadMax'))
            fechaNacimientoMax = datetime.today().replace(day=1,month=1,year=anioMaximo)
            users = users.filter(fechaNacimiento__gte= fechaNacimientoMax)

        if (request.query_params.get('limit') is not None and request.query_params.get('offset') is not None):
            users = users[int(request.query_params.get('offset')):int(request.query_params.get('offset'))+int(request.query_params.get('limit'))]

        usersDTO = UsuarioDto.toUsuariosDto(users)
        serializer = UsuarioSerializer(usersDTO, many=True)
        
        return Response(serializer.data,status=status.HTTP_200_OK,headers={'X-Total-Count' : users.count()})

    def post(self, request, format=None):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid() and serializer.validated_data.get('name') is not None and serializer.validated_data.get('email') is not None and serializer.validated_data.get('password') is not None:
            usuario = Usuario(name=serializer.validated_data.get('name'),
            email=serializer.validated_data.get('email'),
            apellidos=serializer.validated_data.get('apellidos'),
            imagen=serializer.validated_data.get('imagen'),
            fechaNacimiento=serializer.validated_data.get('fechaNacimiento'))
            usuario.set_password(serializer.validated_data.get('password'))
        else:
            return Response({'mensaje' : 'Campos no validos'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            usuario.save()
        except:
            return Response({'mensaje':'Error, ese correo existe'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_201_CREATED)

class UsuarioIDView(APIView):
    def get(self, request, id, format=None):
        try:
            user = Usuario.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        userDTO = UsuarioDto(user)
        serializer = UsuarioSerializer(userDTO)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id, format=None):
        try:
            user = Usuario.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self,request, id, format=None):
        try:
            user = Usuario.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
   

        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            if (serializer.validated_data.get('name') is not None):
                user.name = serializer.validated_data.get('name')
                
            if (serializer.validated_data.get('email') is not None):
                user.email = serializer.validated_data.get('email')
            
            if (serializer.validated_data.get('apellidos') is not None):
                user.apellidos = serializer.validated_data.get('apellidos')
                
            if (serializer.validated_data.get('imagen') is not None):
                user.imagen = serializer.validated_data.get('imagen')

            if (serializer.validated_data.get('fechaNacimiento') is not None):
                user.fechaNacimiento = serializer.validated_data.get('fechaNacimiento')
                
            if (serializer.validated_data.get('password') is not None):
                user.set_password(serializer.validated_data.get('password'))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            user.save()
        except:
            return Response({'mensage':'Error, ese correo existe'}, status=status.HTTP_400_BAD_REQUEST)
    
        return Response(status=status.HTTP_200_OK)

class VehiculoView(APIView):
    def get(self, request, format=None):
        vehiculos = Vehiculo.objects.all()

        if request.query_params.get('modelo') is not None:
           vehiculos =  vehiculos.filter(modelo__icontains=request.query_params.get('modelo'))
        
        if request.query_params.get('matricula') is not None:
           vehiculos =  vehiculos.filter(matricula__icontains=request.query_params.get('matricula'))
        
        if request.query_params.get('color') is not None:
           vehiculos =  vehiculos.filter(color__icontains=request.query_params.get('color'))
        
        if request.query_params.get('plazas') is not None:
           vehiculos =  vehiculos.filter(plazas=int(request.query_params.get('plazas')))
        
        if (request.query_params.get('limit') is not None and request.query_params.get('offset') is not None):
            vehiculos = vehiculos[int(request.query_params.get('offset')):int(request.query_params.get('offset'))+int(request.query_params.get('limit'))]


        vehiculosDTO = VehiculoDto.toVehiculoDto(vehiculos)
        serializer = VehiculoSerializer(vehiculosDTO, many=True)
        
        return Response(serializer.data,status=status.HTTP_200_OK,headers={'X-Total-Count' : vehiculos.count()})
    
    def post(self, request, format=None):
        serializer = VehiculoSerializer(data=request.data)
        if serializer.is_valid() and serializer.validated_data.get('usuario') is not None and serializer.validated_data.get('modelo') is not None and serializer.validated_data.get('matricula') is not None and serializer.validated_data.get('plazas') is not None:
            try:
                usuario = Usuario.objects.get(id=serializer.validated_data.get('usuario').get('id'))
            except:
                return Response({'mensaje' : 'El usuario no existe'})
            
            vehiculo = Vehiculo(usuario=usuario,
            modelo=serializer.validated_data.get('modelo'),
            color=serializer.validated_data.get('color'),
            matricula=serializer.validated_data.get('matricula'),
            imagen=serializer.validated_data.get('imagen'),
            plazas=serializer.validated_data.get('plazas'))
        else:
            return Response({'mensaje' : 'Campos no validos'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            vehiculo.save()
        except:
            return Response({'mensaje':'No se ha podido crear el vehiculo'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_201_CREATED)

class VehiculoIDView(APIView):
    def get(self, request, id, format=None):
        try:
            vehiculo = Vehiculo.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        vehiculoDto = VehiculoDto(vehiculo)
        serializer = VehiculoSerializer(vehiculoDto)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def delete(self, request, id, format=None):
        try:
            vehiculo = Vehiculo.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        vehiculo.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self,request, id, format=None):
        try:
            vehiculo = Vehiculo.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
   

        serializer = VehiculoSerializer(data=request.data)
        if serializer.is_valid():
            if (serializer.validated_data.get('usuario') is not None):
                try:
                    usuario = Usuario.objects.get(id=serializer.validated_data.get('usuario').get('id'))
                except:
                    return Response({'mensaje' : 'El usuario no existe'})
                vehiculo.usuario = usuario
                
            if (serializer.validated_data.get('modelo') is not None):
                vehiculo.email = serializer.validated_data.get('modelo')
            
            if (serializer.validated_data.get('apellidos') is not None):
                vehiculo.apellidos = serializer.validated_data.get('apellidos')
                
            if (serializer.validated_data.get('color') is not None):
                vehiculo.color = serializer.validated_data.get('color')

            if (serializer.validated_data.get('matricula') is not None):
                vehiculo.fechaNacimiento = serializer.validated_data.get('matricula')
                
            if (serializer.validated_data.get('imagen') is not None):
                vehiculo.imagen = serializer.validated_data.get('imagen')

            if (serializer.validated_data.get('plazas') is not None):
                vehiculo.plazas = serializer.validated_data.get('plazas')
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            vehiculo.save()
        except:
            return Response({'mensage':'No se ha podido modificar el vehiculo'}, status=status.HTTP_400_BAD_REQUEST)
    
        return Response(status=status.HTTP_200_OK)


        
class TrayectoView(APIView):
    def get(self, request, format=None):
        trayectos = Trayecto.objects.all()
            
        trayectoDTO = TrayectoDto.toTrayectoDto(trayectos)
        serializer = TrayectoSerializer(trayectoDTO, many=True)
        
        return Response(serializer.data,status=status.HTTP_200_OK,headers={'X-Total-Count' : trayectos.count()})

    def post(self, request, format=None):
        serializer = TrayectoSerializer(data=request.data)
        if serializer.is_valid() and serializer.validated_data.get('piloto') is not None and serializer.validated_data.get('origen') is not None and serializer.validated_data.get('destino') is not None and serializer.validated_data.get('vehiculo') is not None and serializer.validated_data.get('fechaSalida') is not None:
            try:
                piloto = Usuario.objects.get(id=serializer.validated_data.get('piloto').get('id'))
            except:
                return Response({'mensaje' : 'El usuario no existe'})

            try:
                origen = Ubicacion.objects.get(id=serializer.validated_data.get('origen').get('id'))
            except:
                return Response({'mensaje' : 'Buscamos coordenadas'})
                #Aqui viene cuando buscamos la longitud y la latitud en open street map CREO
            
            try:
                destino = Ubicacion.objects.get(id=serializer.validated_data.get('destino').get('id'))
            except:
                return Response({'mensaje' : 'Buscamos coordenadas'})
                #Aqui viene cuando buscamos la longitud y la latitud en open street map CREO
            
            try:
                vehiculo = Vehiculo.objects.get(id=serializer.validated_data.get('vehiculo').get('id'))
                if vehiculo.usuario.id != piloto.id:
                    return Response({'mensaje' : 'El vehiculo no pertenece al piloto'})
                    #Lanzamos una excepcion de que no puedes poner un vehiculo de otro usuario
            except:
                return Response({'mensaje' : 'Buscamos coordenadas'})
                
            
            trayecto = Trayecto(origen = origen,
               # paradas = paradas,
                destino = destino,
                piloto = piloto,
                vehiculo = vehiculo,
                precio = serializer.validated_data.get('precio'),
                fechaSalida = serializer.validated_data.get('fechaSalida'))

            try:
                trayecto.save()
            except:
                return Response({'mensaje':'No se ha podido crear el trayecto'}, status=status.HTTP_400_BAD_REQUEST)
                
        else:
            print(serializer.errors)
            return Response({'mensaje' : 'Campos no validos'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_201_CREATED)

class TrayectoIDView(APIView):
    def get(self, request, id, format=None):
        try:
            trayecto = Trayecto.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        trayectoDto = TrayectoDto(trayecto)
        serializer = TrayectoSerializer(trayectoDto)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def delete(self, request, id, format=None):
        try:
            trayecto = Trayecto.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        trayecto.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self,request, id, format=None):
        try:
            trayecto = Trayecto.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = TrayectoSerializer(data=request.data)

        if serializer.is_valid():

            if (serializer.validated_data.get('origen') is not None):
                try:
                    origen = Ubicacion.objects.get(id=serializer.validated_data.get('origen').get('id'))
                except:
                    return Response({'mensaje' : 'El rigen no existe'})
                trayecto.origen = origen

            #if (serializer.validated_data.get('paradas') is not None):
            #    trayecto.paradas = serializer.validated_data.get('paradas')
            
            if (serializer.validated_data.get('destino') is not None):
                try:
                    destino = Ubicacion.objects.get(id=serializer.validated_data.get('destino').get('id'))
                except:
                    return Response({'mensaje' : 'El destino no existe'})
                trayecto.destino = destino

            if (serializer.validated_data.get('piloto') is not None):
                try:
                    piloto = Usuario.objects.get(id=serializer.validated_data.get('piloto').get('id'))
                except:
                    return Response({'mensaje' : 'El piloto no existe'})
                trayecto.piloto = piloto

            if (serializer.validated_data.get('vehiculo') is not None):
                try:
                    vehiculo = Vehiculo.objects.get(id=serializer.validated_data.get('vehiculo').get('id'))
                except:
                    return Response({'mensaje' : 'El vehiculo no existe'})
                trayecto.vehiculo = vehiculo
                
            if (serializer.validated_data.get('precio') is not None):
                trayecto.precio = serializer.validated_data.get('precio')

            if (serializer.validated_data.get('plazas') is not None):
                trayecto.plazas = serializer.validated_data.get('plazas')
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            trayecto.save()
        except:
            return Response({'mensage':'No se ha podido modificar el trayecto'}, status=status.HTTP_400_BAD_REQUEST)
    
        return Response(status=status.HTTP_200_OK)