import json
from urllib.request import Request
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from zoomcar.dto import ReservaDto, UsuarioDto, VehiculoDto, TrayectoDto, ComentarioDto
from zoomcar.serializers import GasolineraSerializer, ReservaSerializer, UsuarioSerializer, VehiculoSerializer, TrayectoSerializer, ComentarioSerializer
from zoomcar.models import Reserva, Usuario, Vehiculo, Trayecto, Ubicacion, Comentario
from datetime import date, datetime
import requests
from geopy import distance,Nominatim
import unicodedata
from pyproj import Transformer
from google.oauth2 import id_token
from google.auth import transport
import pytz

URL_GASOLINERAS = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
URL_AEMET = "https://opendata.aemet.es/opendata/api/"
API_KEY_AEMET = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbnRvbmlvc2RAdW1hLmVzIiwianRpIjoiNTk0MTE3ZWYtM2UxYi00MTExLTliN2UtNjk3MDczNTdjNDI5IiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE2MzU1OTA2NTIsInVzZXJJZCI6IjU5NDExN2VmLTNlMWItNDExMS05YjdlLTY5NzA3MzU3YzQyOSIsInJvbGUiOiIifQ.5qkhM2s0Zwd81shKKo5QnTNDrZIUGVrIrwwp_bdMkX4"
USER_AGENT = "https://www.zoomcar.es/geocoding?email=nicolasqm@uma.es"
URL_INCIDENCIAS_TRAFICO = "https://services1.arcgis.com/nCKYwcSONQTkPA4K/arcgis/rest/services/incidencias_DGT/FeatureServer/0/query"
CLIENT_ID = "860266555787-337c130jdi6jar97gkmomb1dq71sv02i.apps.googleusercontent.com"
GASOLINERA_RESPONSE = None
GASOLINERA_TIMESTAMP = 0

MUNICIPIOS_RESPONSE = None


def autorizar(request):
    if request.headers.get('Authorization') is not None:
            
        token = request.headers.get('Authorization')
        idinfo = None
        try:
            idinfo = id_token.verify_oauth2_token(token, transport.requests.Request(), CLIENT_ID)
        except:
            return None

        email = idinfo['email']

        try:
            usuario = Usuario.objects.get(email=email)
            return usuario
        except:
            return None
    else :
        return None


### Usuario ###
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
        usuario = autorizar(request)
        if usuario is None:
            return Response({"mensaje" : "Es necesario el header Authorization"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = Usuario.objects.get(id=id)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)

        if usuario.id != user.id:
            return Response({"mensaje" : "No tienes permiso"}, status=status.HTTP_403_FORBIDDEN)

        user.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self,request, id, format=None):
        usuario = autorizar(request)
        if usuario is None:
            return Response({"mensaje":"Es necesario el header de autorizacion"},status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            user = Usuario.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if usuario.id != user.id:
            return Response({"mensaje":"No tienes permiso"},status=status.HTTP_401_UNAUTHORIZED)

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

            if (serializer.validated_data.get('twitterToken') is not None):
                user.twitterToken = serializer.validated_data.get('twitterToken')
                
            if (serializer.validated_data.get('password') is not None):
                user.set_password(serializer.validated_data.get('password'))
                
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            user.save()
        except:
            return Response({'mensaje':'Error, ese correo existe'}, status=status.HTTP_400_BAD_REQUEST)
    
        return Response(status=status.HTTP_204_NO_CONTENT)

#=================================================================================================================
#=================================================================================================================
#=================================================================================================================
#=================================================================================================================
#=================================================================================================================
#=================================================================================================================

### Vehiculo ###
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
        usuario = autorizar(request)

        if usuario is None:
            return Response({"mensaje" : "Es necesario el header Authorization"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = VehiculoSerializer(data=request.data)
        if serializer.is_valid() and serializer.validated_data.get('modelo') is not None and serializer.validated_data.get('matricula') is not None and serializer.validated_data.get('plazas') is not None:
            
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
        usuario = autorizar(request)
        if usuario is None:
            return Response({"mensaje" : "Es necesario el header Authorization"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            vehiculo = Vehiculo.objects.get(id=id)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        if usuario.id != vehiculo.usuario.id:
            return Response({"mensaje":"No tien permiso"},status=status.HTTP_401_UNAUTHORIZED)

        vehiculo.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self,request, id, format=None):
        usuario = autorizar(request)
        if usuario is None:
            return Response({"mensaje" : "Es necesario el header Authorization"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            vehiculo = Vehiculo.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if usuario.id != vehiculo.usuario.id:
            return Response({"mensaje":"No tien permiso"},status=status.HTTP_401_UNAUTHORIZED)

        serializer = VehiculoSerializer(data=request.data)
        if serializer.is_valid():
            if (serializer.validated_data.get('usuario') is not None):
                try:
                    usuario = Usuario.objects.get(id=serializer.validated_data.get('usuario').get('id'))
                except:
                    return Response({'mensaje' : 'El usuario no existe'},status=status.HTTP_400_BAD_REQUEST)
                vehiculo.usuario = usuario
                
            if (serializer.validated_data.get('modelo') is not None):
                vehiculo.modelo = serializer.validated_data.get('modelo')
                
            if (serializer.validated_data.get('color') is not None):
                vehiculo.color = serializer.validated_data.get('color')

            if (serializer.validated_data.get('matricula') is not None):
                vehiculo.matricula = serializer.validated_data.get('matricula')
                
            if (serializer.validated_data.get('imagen') is not None):
                vehiculo.imagen = serializer.validated_data.get('imagen')

            if (serializer.validated_data.get('plazas') is not None):
                vehiculo.plazas = serializer.validated_data.get('plazas')
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            vehiculo.save()
        except:
            return Response({'mensaje':'No se ha podido modificar el vehiculo'}, status=status.HTTP_400_BAD_REQUEST)
    
        return Response(status=status.HTTP_204_NO_CONTENT)

#=================================================================================================================
#=================================================================================================================
#=================================================================================================================
#=================================================================================================================
#=================================================================================================================
#=================================================================================================================

### Trayecto ###
def getMunicipio(latitud,longitud):
    geolocator = Nominatim(user_agent=USER_AGENT)
    origen = geolocator.reverse(str(latitud) + ', ' + str(longitud))
    if origen.raw.get('address').get('city') is None:
        return str(unicodedata.normalize('NFKD',origen.raw.get('address').get('town')).encode('ASCII','ignore').strip().decode('utf-8'))
    else:
        return str(unicodedata.normalize('NFKD',origen.raw.get('address').get('city')).encode('ASCII','ignore').strip().decode('utf-8'))
   
        
class TrayectoView(APIView):
    def get(self, request, format=None):
        trayectos = Trayecto.objects.all()

        if request.query_params.get('precioMin') is not None:
            precioMin = float(request.query_params.get('precioMin'))
            trayectos = trayectos.filter(precio__gte = precioMin)
        
        if request.query_params.get('precioMax') is not None:
            precioMax = float(request.query_params.get('precioMax'))
            trayectos = trayectos.filter(precio__lte = precioMax)
        
        if(request.query_params.get('fechaMin') is not None):
            fechaMin = request.query_params.get('fechaMin')
            trayectos = trayectos.filter(fechaSalida__gte = fechaMin)

        if(request.query_params.get('fechaMax') is not None):
            fechaMax = request.query_params.get('fechaMax')
            trayectos = trayectos.filter(fechaSalida__lte = fechaMax)

        if (request.query_params.get('origen') is not None):
            origen = str(unicodedata.normalize('NFKD',request.query_params.get('origen')).encode('ASCII','ignore').strip().decode('utf-8'))
            trayectos = trayectos.filter(origen__municipio__icontains=origen)

        if (request.query_params.get('destino') is not None):
            destino = str(unicodedata.normalize('NFKD',request.query_params.get('destino')).encode('ASCII','ignore').strip().decode('utf-8'))
            trayectos = trayectos.filter(destino__municipio__icontains=destino)

        if (request.query_params.get('limit') is not None and request.query_params.get('offset') is not None):
            trayectos = trayectos[int(request.query_params.get('offset')):int(request.query_params.get('offset'))+int(request.query_params.get('limit'))]
            
        trayectoDTO = TrayectoDto.toTrayectoDto(trayectos)
        serializer = TrayectoSerializer(trayectoDTO, many=True)
        
        return Response(serializer.data,status=status.HTTP_200_OK,headers={'X-Total-Count' : trayectos.count()})

    def post(self, request, format=None):
        usuario = autorizar(request)
        if usuario is None:
            return Response({"mensaje":"Es necesario el header de autorizacion"},status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = TrayectoSerializer(data=request.data)
        if serializer.is_valid() and serializer.validated_data.get('origen') is not None and serializer.validated_data.get('destino') is not None and serializer.validated_data.get('vehiculo') is not None and serializer.validated_data.get('fechaSalida') is not None:
            try:
                origen = Ubicacion.objects.get(latitud=serializer.validated_data.get('origen').get('latitud'), longitud=serializer.validated_data.get('origen').get('longitud'))
            except:
                origen = Ubicacion(latitud=float(serializer.validated_data.get('origen').get('latitud')),longitud=float(serializer.validated_data.get('origen').get('longitud')),
                municipio=getMunicipio(float(serializer.validated_data.get('origen').get('latitud')),float(serializer.validated_data.get('origen').get('longitud'))))
                origen.save()
            
            try:
                destino = Ubicacion.objects.get(latitud=serializer.validated_data.get('destino').get('latitud'), longitud=serializer.validated_data.get('destino').get('longitud'))
            except:
                destino = Ubicacion(latitud=float(serializer.validated_data.get('destino').get('latitud')),longitud=float(serializer.validated_data.get('destino').get('longitud')),
                municipio=getMunicipio(float(serializer.validated_data.get('destino').get('latitud')),float(serializer.validated_data.get('destino').get('longitud'))))
                destino.save()

            paradasBD = []
            for parada in serializer.validated_data.get('paradas'):
                try:
                    paradaBD = Ubicacion.objects.get(latitud=parada.get('latitud'),longitud=parada.get('longitud'))
                except:
                    paradaBD = Ubicacion(latitud=parada.get('latitud'),longitud=parada.get('longitud'),
                    municipio = getMunicipio(parada.get('latitud'),parada.get('longitud')))
                    paradaBD.save()
                paradasBD.append(paradaBD)
            
            try:
                vehiculo = Vehiculo.objects.get(id=serializer.validated_data.get('vehiculo').get('id'))
                if vehiculo.usuario.id != usuario.id:
                    return Response({'mensaje' : 'El vehiculo no pertenece al piloto'}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({'mensaje' : 'El vehiculo no existe'}, status=status.HTTP_400_BAD_REQUEST)
                
            
            

            trayecto = Trayecto(origen = origen,
                destino = destino,
                piloto = usuario,
                vehiculo = vehiculo,
                precio = serializer.validated_data.get('precio'),
                fechaSalida = serializer.validated_data.get('fechaSalida'))
            try:
                trayecto.save()
                trayecto.paradas.add(*paradasBD)

                if usuario.twitterToken is not None:
                    url = 'https://api.twitter.com/2/tweets'
                    text = 'He publicado un nuevo viaje desde ' + trayecto.origen.municipio + ' a ' + trayecto.destino.municipio + ", echale un vistazo en https://zoomcar-iweb.herokuapp.com/trayectos/" + str(trayecto.id)
                    headers = {
                        'Content-type': 'application/json',
                        'Authorization' : 'Bearer ' + usuario.twitterToken
                    }
                    response = requests.post(url, json={'text': text}, headers=headers)
            except:
                return Response({'mensaje':'No se ha podido crear el trayecto'}, status=status.HTTP_400_BAD_REQUEST)
                
        else:
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
        usuario = autorizar(request)
        if usuario is None:
            return Response({"mensaje" : "Es necesario el header Authorization"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            trayecto = Trayecto.objects.get(id=id)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        if usuario.id != trayecto.piloto.id:
            return Response({"mensaje":"No tien permiso"},status=status.HTTP_401_UNAUTHORIZED)

        trayecto.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
        


    def put(self,request, id, format=None):
        usuario = autorizar(request)
        if usuario is None:
            return Response({"mensaje" : "Es necesario el header Authorization"}, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            trayecto = Trayecto.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if usuario.id != trayecto.piloto.id:
            return Response({"mensaje":"No tiene permiso"},status=status.HTTP_401_UNAUTHORIZED)

        serializer = TrayectoSerializer(data=request.data)

        if serializer.is_valid():

            if (serializer.validated_data.get('origen') is not None):
                
                try:
                    origen = Ubicacion.objects.get(latitud=serializer.validated_data.get('origen').get('latitud'), longitud=serializer.validated_data.get('origen').get('longitud'))
                except:
                    origen = Ubicacion(latitud=float(serializer.validated_data.get('origen').get('latitud')),longitud=float(serializer.validated_data.get('origen').get('longitud')),
                    municipio=getMunicipio(float(serializer.validated_data.get('origen').get('latitud')),float(serializer.validated_data.get('origen').get('longitud'))))
                    origen.save()
                trayecto.origen = origen

            if (serializer.validated_data.get('destino') is not None):
                try:
                    destino = Ubicacion.objects.get(latitud=serializer.validated_data.get('destino').get('latitud'), longitud=serializer.validated_data.get('destino').get('longitud'))
                except:
                    destino = Ubicacion(latitud=float(serializer.validated_data.get('destino').get('latitud')),longitud=float(serializer.validated_data.get('destino').get('longitud')),
                    municipio=getMunicipio(float(serializer.validated_data.get('destino').get('latitud')),float(serializer.validated_data.get('destino').get('longitud'))))
                    destino.save()
                trayecto.destino = destino

            if (serializer.validated_data.get('piloto') is not None):
                try:
                    piloto = Usuario.objects.get(id=serializer.validated_data.get('piloto').get('id'))
                except:
                    return Response({'mensaje' : 'El piloto no existe'},status=status.HTTP_400_BAD_REQUEST)
                trayecto.piloto = piloto

            if (serializer.validated_data.get('vehiculo') is not None):
                try:
                    vehiculo = Vehiculo.objects.get(id=serializer.validated_data.get('vehiculo').get('id'))
                except:
                    return Response({'mensaje' : 'El vehiculo no existe'},status=status.HTTP_400_BAD_REQUEST)
                trayecto.vehiculo = vehiculo
            
            if serializer.validated_data.get('paradas') is not None:
                trayecto.paradas.clear()
                paradasBD = []
                for parada in serializer.validated_data.get('paradas'):
                    try:
                        paradaBD = Ubicacion.objects.get(latitud=parada.get('latitud'),longitud=parada.get('longitud'))
                    except:
                        paradaBD = Ubicacion(latitud=parada.get('latitud'),longitud=parada.get('longitud'),
                        municipio = getMunicipio(parada.get('latitud'),parada.get('longitud')))
                        paradaBD.save()

                    paradasBD.append(paradaBD)
                    
                try:
                    trayecto.paradas.add(*paradasBD)
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                
            if (serializer.validated_data.get('precio') is not None):
                trayecto.precio = serializer.validated_data.get('precio')

            if (serializer.validated_data.get('fechaSalida') is not None):
                trayecto.fechaSalida = serializer.validated_data.get('fechaSalida')

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            trayecto.save()
        except:
            return Response({'mensaje':'No se ha podido modificar el trayecto'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

#============================================================================================================================
#============================================================================================================================
#============================================================================================================================
#============================================================================================================================
#============================================================================================================================
#============================================================================================================================

### Consultas de entidades relacionadas ###

class VehiculosUsuarioView (APIView):
    def get(self,request,id,format=None):
        try:
            user = Usuario.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        vehiculos = user.vehiculo_set.all()

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

        vehiculosDto = VehiculoDto.toVehiculoDto(vehiculos)
        serializers = VehiculoSerializer(vehiculosDto,many=True)

        return Response(serializers.data,status=status.HTTP_200_OK,headers={'X-Total-Count' : vehiculos.count()})

class TrayectosUsuarioView (APIView):
    def get(self,request,id,format=None):
        try:
            user = Usuario.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        trayectos = user.trayecto_set.all()

        if request.query_params.get('precioMin') is not None:
            precioMin = float(request.query_params.get('precioMin'))
            trayectos = trayectos.filter(precio__gte = precioMin)
        
        if request.query_params.get('precioMax') is not None:
            precioMax = float(request.query_params.get('precioMax'))
            trayectos = trayectos.filter(precio__lte = precioMax)
        
        if(request.query_params.get('fechaMin') is not None):
            fechaMin = request.query_params.get('fechaMin')
            trayectos = trayectos.filter(fechaSalida__gte = fechaMin)

        if(request.query_params.get('fechaMax') is not None):
            fechaMax = request.query_params.get('fechaMax')
            trayectos = trayectos.filter(fechaSalida__lte = fechaMax)

        if (request.query_params.get('origen') is not None):
            origen = str(unicodedata.normalize('NFKD',request.query_params.get('origen')).encode('ASCII','ignore').strip().decode('utf-8'))
            trayectos = trayectos.filter(origen__municipio__icontains=origen)

        if (request.query_params.get('destino') is not None):
            destino = str(unicodedata.normalize('NFKD',request.query_params.get('destino')).encode('ASCII','ignore').strip().decode('utf-8'))
            trayectos = trayectos.filter(destino__municipio__icontains=destino)

        if (request.query_params.get('limit') is not None and request.query_params.get('offset') is not None):
            trayectos = trayectos[int(request.query_params.get('offset')):int(request.query_params.get('offset'))+int(request.query_params.get('limit'))]

        trayectosDto = TrayectoDto.toTrayectoDto(trayectos)
        serializers = TrayectoSerializer(trayectosDto,many=True)

        return Response(serializers.data,status=status.HTTP_200_OK,headers={'X-Total-Count' : trayectos.count()})

#============================================================================================================================
#============================================================================================================================
#============================================================================================================================
#============================================================================================================================
#============================================================================================================================
#============================================================================================================================

### Datos abiertos ###

def getDistancia(latitudO,longitudO,latitudD,longitudD):
    coords_1 = (latitudO,longitudO)
    coords_2 = (latitudD,longitudD)

    return distance.distance(coords_1,coords_2).km

class GasolineraAPIView(APIView):
    def get(self,request,format=None):
        
        if request.query_params.get('longitud'):
            longitud = float(request.query_params.get('longitud'))
        else:
            return Response({"mensaje":"Falta el campo longitud"},status=status.HTTP_400_BAD_REQUEST)
        if request.query_params.get('latitud'):
            latitud = float(request.query_params.get('latitud'))
        else:
            return Response({"mensaje":"Falta el campo latitud"},status=status.HTTP_400_BAD_REQUEST)
        
        if request.query_params.get('distancia'):
            distancia = float(request.query_params.get('distancia'))
        else:
            return Response({"mensaje":"Falta el campo distancia"},status=status.HTTP_400_BAD_REQUEST)
        
        now = datetime.timestamp(datetime.now())

        global GASOLINERA_RESPONSE
        global GASOLINERA_TIMESTAMP

        # Actualizar respuesta cacheada cada media hora
        if (now - GASOLINERA_TIMESTAMP >= 1800):
            GASOLINERA_RESPONSE = requests.get(URL_GASOLINERAS,headers={"Content-Type" : "application/json"})
            GASOLINERA_TIMESTAMP = now
        
        json = GASOLINERA_RESPONSE.json()
        
        gasolinerasFiltro = []
        for gasolinera in json.get('ListaEESSPrecio'):
            latitudD = float(gasolinera.get('Latitud').replace(',','.'))
            longitudD = float(gasolinera.get('Longitud (WGS84)').replace(',','.'))
            if (getDistancia(latitudO=latitud,longitudO=longitud,latitudD=latitudD,longitudD=longitudD) <= distancia):
                gasolinerasFiltro.append(gasolinera)

        gasolinerasResponse = GasolineraSerializer(gasolinerasFiltro,many=True)
        return Response(gasolinerasResponse.data,status=status.HTTP_200_OK)


def getMunicipioID(json,nombre):
    nombre = unicodedata.normalize('NFKD',nombre).encode('ASCII','ignore').strip().lower()
    for municipio in json:
        nombreM = unicodedata.normalize('NFKD',municipio.get('nombre')).encode('ASCII','ignore').strip().lower()
        if (nombreM == nombre):
            return municipio.get('id')[2:]
    
    return None

def getTiempo (json, fecha, hora):
    predicciones = json[0].get('prediccion')
    pPrecipitacion = ""
    eCielo = ""
    vientoValores = ""
    temperaturaMax = ""
    temperaturaMin = ""
    for diaPrediccion in predicciones.get('dia'):
        if (fecha in diaPrediccion.get('fecha')):
            probPrecipitacion = diaPrediccion.get('probPrecipitacion')
            for periodo in probPrecipitacion:
                if periodo.get('periodo') is not None:
                    pMin = int(periodo.get('periodo')[0:2])
                    pMax = int(periodo.get('periodo')[3:])
                    if hora > pMin and hora < pMax:
                        pPrecipitacion = periodo.get('value')
                else:
                    pPrecipitacion = periodo.get('value')

            estadoCielo = diaPrediccion.get('estadoCielo')
            for periodo in estadoCielo:
                if periodo.get('periodo') is not None:
                    pMin = int(periodo.get('periodo')[0:2])
                    pMax = int(periodo.get('periodo')[3:])
                    if hora > pMin and hora < pMax:
                        eCielo = periodo.get('descripcion')
                else:
                    eCielo = periodo.get('descripcion')
            
            viento = diaPrediccion.get('viento')

            for periodo in viento:
                if periodo.get('periodo') is not None:
                    pMin = int(periodo.get('periodo')[0:2])
                    pMax = int(periodo.get('periodo')[3:])
                    if hora > pMin and hora < pMax:
                        vientoValores = {"velocidad":periodo.get('velocidad'),"direccion":periodo.get('direccion')}
                else:
                    vientoValores = {"velocidad":periodo.get('velocidad'),"direccion":periodo.get('direccion')}

            temperaturaMax = diaPrediccion.get('temperatura').get('maxima')
            temperaturaMin = diaPrediccion.get('temperatura').get('minima')

            return {'probPrecipitacion':pPrecipitacion,'estadoCielo':eCielo,'viento':vientoValores,'temperaturaMax':temperaturaMax,'temperaturaMin':temperaturaMin}
    return None


class TiempoView(APIView):
    def get(self,request,format=None):

        if request.query_params.get('municipio'):
            municipio = request.query_params.get('municipio')
        else:
            return Response({"mensaje":"Falta el campo municipio"},status=status.HTTP_400_BAD_REQUEST)
        
        if request.query_params.get('fecha'):
            fecha = request.query_params.get('fecha')
        else:
            return Response({"mensaje":"Falta el campo fecha"},status=status.HTTP_400_BAD_REQUEST)
        
        if request.query_params.get('hora'):
            hora = int(request.query_params.get('hora'))
        else:
            return Response({"mensaje":"Falta el campo hora"},status=status.HTTP_400_BAD_REQUEST)
        
        global MUNICIPIOS_RESPONSE

        # Cacheamos listado de municipios
        if MUNICIPIOS_RESPONSE is None:
            MUNICIPIOS_RESPONSE = requests.get(URL_AEMET + "/maestro/municipios",headers={"Content-Type" : "application/json","api_key":API_KEY_AEMET})

        municipioID = getMunicipioID(MUNICIPIOS_RESPONSE.json(), municipio)

        if municipioID is None :
            return Response({"mensaje" : "El nombre del municipio es incorrecto"},status=status.HTTP_400_BAD_REQUEST)

        respuestaMunicipio = requests.get(URL_AEMET + "/prediccion/especifica/municipio/diaria/" + municipioID,headers={"Content-Type" : "application/json","api_key":API_KEY_AEMET})

        urlAcceso = respuestaMunicipio.json().get('datos')

        respuestaDatosTiempo = requests.get(urlAcceso,headers={"Content-Type" : "application/json"})

        respuestaJson = getTiempo(respuestaDatosTiempo.json(),fecha,hora)

        if respuestaJson is None:
            return Response({"mensaje" : "El dia no se puede predecir aun"},status=status.HTTP_400_BAD_REQUEST)

        return Response(respuestaJson, status=status.HTTP_200_OK)

class IncidenciasTraficoAPIView(APIView):
    def get(self,request,format=None):
        if request.query_params.get('municipio') is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        municipio = request.query_params.get('municipio')
        respuesta = requests.get(URL_INCIDENCIAS_TRAFICO + "?f=json&where=(poblacion%20IN%20(%27" + municipio + "%27))&outFields=poblacion,fechahora_,carretera,causa")
        
        json = respuesta.json().get('features')
        
        incidenciasTotales = []
        transformer = Transformer.from_crs("epsg:3857","epsg:4326")
        for features in json:
            attributes = features.get('attributes')
            latitud, longitud = transformer.transform(float(features.get('geometry').get('x')), float(features.get('geometry').get('y')))
            incidenciasTotales.append({'poblacion' : attributes.get('poblacion'), 'fecha' : attributes.get('fechahora_'), 'carretera' : attributes.get('carretera'), 'causa' : attributes.get('causa'), 'latitud' : latitud, 'longitud' : longitud})

        return Response(incidenciasTotales,status=status.HTTP_200_OK)

#============================================================================================================================
#============================================================================================================================
#============================================================================================================================
#============================================================================================================================
#============================================================================================================================
#============================================================================================================================

# Google Login

class LoginGoogle(APIView):
    def post(self,request,format=None):
        if request.headers.get('Authorization') is not None:
            
            token = request.headers.get('Authorization')
            idinfo = None
            try:
                idinfo = id_token.verify_oauth2_token(token, transport.requests.Request(), CLIENT_ID)
            except:
                return Response({"mensaje": "Token caducado"}, status=status.HTTP_400_BAD_REQUEST)

            email = idinfo['email']
            usuario = None

            try:
                usuario = Usuario.objects.get(email=email)
            except:

                name = idinfo['given_name']
                try:
                    apellidos = idinfo['family_name']
                except:
                    apellidos = ""
                imagen = idinfo['picture']

                
                usuario = Usuario(
                    email = email,
                    name = name,
                    apellidos = apellidos,
                    imagen = imagen,
                    fechaNacimiento = date.today(),
                    twitterToken = None
                )

                usuario.save()

            userDTO = UsuarioDto(usuario)
            serializer = UsuarioSerializer(userDTO)
            return Response(serializer.data,status=status.HTTP_200_OK)

        else :
            return Response({"mensaje" : "Es necesario el header Authorization"}, status=status.HTTP_400_BAD_REQUEST)

class LoginGoogleCheckView(APIView):
    def post(self,request,format=None):
        if request.headers.get('Authorization') is not None:
            
            token = request.headers.get('Authorization')
            idinfo = None
            try:
                id_token.verify_oauth2_token(token, transport.requests.Request(), CLIENT_ID)
            except:
                return Response({"mensaje": "caducado"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"mensaje" : "ok"},status=status.HTTP_200_OK)

        else :
            return Response({"mensaje" : "header"}, status=status.HTTP_400_BAD_REQUEST)

# Reservas

class ReservasView(APIView):
    def post(self,request, format=None):
        usuario = autorizar(request)
        if usuario is None:
            return Response({"mensaje" : "Es necesario el header Authorization"}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = ReservaSerializer(data=request.data)
        if serializer.is_valid():
            try:
                trayecto = Trayecto.objects.get(id=serializer.validated_data.get('trayecto').get('id'))
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)
                
            utc = pytz.UTC
            now = utc.localize(datetime.now())
            
            if trayecto.fechaSalida < now:
                return Response({"mensaje" : "Ha pasado la fecha"}, status=status.HTTP_400_BAD_REQUEST)

            if trayecto.reserva_set.all().count() >= trayecto.vehiculo.plazas - 1:
                return Response({"mensaje" : "Limite de plazas"}, status=status.HTTP_400_BAD_REQUEST)

            reserva = Reserva(
                trayecto = trayecto,
                usuario = usuario
            )

            reserva.save()
        else:
            return Response({"mensaje" : "Campos incorrectos"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)

#Eliminar reservas
class ReservaIDView(APIView):
    def delete(self,request,id,format=None):
        usuario = autorizar(request)
        if usuario is None:
            return Response({"mensaje" : "Es necesario el header Authorization"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            reserva = Reserva.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if reserva.usuario.id != usuario.id:
            return Response({"mensaje","No estas autorizado para borrarlo"},status=status.HTTP_401_UNAUTHORIZED)
        
        reserva.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Reservas de una persona /usuarios/{id}/reservas
class ReservasUsuarioView(APIView):
    def get(self,request,id,format=None):
        
        reservas = Reserva.objects.filter(usuario__id=id)
        reservasDTO = ReservaDto.toReservaDto(reservas)
        serializer = ReservaSerializer(reservasDTO, many=True)

        return Response(serializer.data,status=status.HTTP_200_OK,headers={"X-Total-Count":reservas.count()})

# Reservas de un trayecto /trayectos/{id}/reservas
class ReservasTrayectosView(APIView):
    def get(self,request,id,format=None):
        
        reservas = Reserva.objects.filter(trayecto__id=id)
        reservasDTO = ReservaDto.toReservaDto(reservas)
        serializer = ReservaSerializer(reservasDTO, many=True)

        return Response(serializer.data,status=status.HTTP_200_OK,headers={"X-Total-Count":reservas.count()})

# Comentarios
class ComentarioView(APIView):
    def post(self,request, format=None):
        usuario = autorizar(request)
        if usuario is None:
            return Response({"mensaje" : "Es necesario el header Authorization"}, status=status.HTTP_401_UNAUTHORIZED)
            
        serializers = ComentarioSerializer(data=request.data)
        if serializers.is_valid():
            try:
                user = Usuario.objects.get(id=serializers.validated_data.get("usuario").get("id"))
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)
            
            comentario = Comentario(
                creador= usuario,
                usuario= user,
                text= serializers.validated_data.get("text")
            )
        else:
            return Response({'mensaje' : 'Campos no validos'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            comentario.save()
        except:
            return Response({"mensaje":"Error al guarda el comentario"},status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

# Comentarios de una persona /usuarios/{id}/comentarios
class ComentarioUsuarioView(APIView):
    def get(self,request,id,format=None):
        comentario = Comentario.objects.filter(usuario__id=id)
        dto = ComentarioDto.toComentarioDto(comentario)
        serializers = ComentarioSerializer(dto,many=True)

        return Response(serializers.data,status=status.HTTP_200_OK,headers={"X-Total-Count":comentario.count()})

class LoginTwitterView(APIView):
    def post(self, request,format=None):
        usuario = autorizar(request)
        if usuario is None:
            return Response({"mensaje" : "Es necesario el header Authorization"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = request.data.get('token')
        except:
            return Response({"mensaje" : "Es necesario el header Token"}, status=status.HTTP_400_BAD_REQUEST)


        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        url = 'https://api.twitter.com/2/oauth2/token?code=' + token + '&grant_type=authorization_code&client_id=a20wU2JuTnE3SGlfSmh0NnAtcDQ6MTpjaQ&redirect_uri=https://zoomcar-iweb.herokuapp.com/loginTwitter&code_verifier=challenge'

        response = requests.post(url,headers)
        json = response.json()

        usuario.twitterToken = json.get('access_token')
        usuario.save()

        return Response(status=status.HTTP_200_OK)