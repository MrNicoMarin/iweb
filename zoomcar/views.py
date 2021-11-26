import geopy
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from zoomcar.dto import UsuarioDto, VehiculoDto, TrayectoDto
from zoomcar.serializers import GasolineraSerializer, UsuarioSerializer, VehiculoSerializer, TrayectoSerializer
from zoomcar.models import Usuario, Vehiculo, Trayecto, Ubicacion
from datetime import datetime
import requests
from geopy import distance
import unicodedata

URL_GASOLINERAS = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
URL_AEMET = "https://opendata.aemet.es/opendata/api/"
API_KEY_AEMET = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbnRvbmlvc2RAdW1hLmVzIiwianRpIjoiNTk0MTE3ZWYtM2UxYi00MTExLTliN2UtNjk3MDczNTdjNDI5IiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE2MzU1OTA2NTIsInVzZXJJZCI6IjU5NDExN2VmLTNlMWItNDExMS05YjdlLTY5NzA3MzU3YzQyOSIsInJvbGUiOiIifQ.5qkhM2s0Zwd81shKKo5QnTNDrZIUGVrIrwwp_bdMkX4"
USER_AGENT = "https://www.zoomcar.es/geocoding?email=nicolasqm@uma.es"
URL_INCIDENCIAS_TRAFICO = "https://services1.arcgis.com/nCKYwcSONQTkPA4K/arcgis/rest/services/incidencias_DGT/FeatureServer/0/query"


#Usuario
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
            return Response({'mensaje':'Error, ese correo existe'}, status=status.HTTP_400_BAD_REQUEST)
    
        return Response(status=status.HTTP_200_OK)

#=================================================================================================================

#Vehiculo
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
            return Response({'mensaje':'No se ha podido modificar el vehiculo'}, status=status.HTTP_400_BAD_REQUEST)
    
        return Response(status=status.HTTP_200_OK)

#============================================================================================================================0

def getMunicipio(latitud,longitud):
    geolocator = geopy.Nominatim(user_agent=USER_AGENT)
    origen = geolocator.reverse(str(latitud) + ', ' + str(longitud))
    if origen.raw.get('address').get('city') is None:
        return origen.raw.get('address').get('town')
    else:
        return origen.raw.get('address').get('city')
   
        
#Trayecto
class TrayectoView(APIView):
    def get(self, request, format=None):
        trayectos = Trayecto.objects.all()

        if request.query_params.get('precioMin') is not None:
            precioMin = int(request.query_params.get('precioMin'))
            trayectos = trayectos.filter(precio__gte = precioMin)
        
        if request.query_params.get('precioMax') is not None:
            precioMax = int(request.query_params.get('precioMax'))
            trayectos = trayectos.filter(precio__lte = precioMax)
        
        if(request.query_params.get('fechaMin') is not None):
            fechaMin = request.query_params('fechaMin')
            trayectos = trayectos.filter(fechaSalida__gte = fechaMin)

        if(request.query_params.get('fechaMax') is not None):
            fechaMax = request.query_params('fechaMax')
            trayectos = trayectos.filter(fechaSalida__lte = fechaMax)
        
            
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
                    return Response({'mensaje' : 'El origen no existe'})
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
            return Response({'mensaje':'No se ha podido modificar el trayecto'}, status=status.HTTP_400_BAD_REQUEST)
    
        return Response(status=status.HTTP_200_OK)

#============================================================================================================================

### Consultas de entidades relacionadas ###

class VehiculosUsuarioView (APIView):
    def get(self,request,id,format=None):
        try:
            user = Usuario.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        vehiculos = user.vehiculo_set.all()
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
        trayectosDto = TrayectoDto.toTrayectoDto(trayectos)
        serializers = TrayectoSerializer(trayectosDto,many=True)

        return Response(serializers.data,status=status.HTTP_200_OK,headers={'X-Total-Count' : trayectos.count()})

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
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.query_params.get('latitud'):
            latitud = float(request.query_params.get('latitud'))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if request.query_params.get('distancia'):
            distancia = float(request.query_params.get('distancia'))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        respuesta = requests.get(URL_GASOLINERAS,headers={"Content-Type" : "application/json"})
        
        json = respuesta.json()
        
        gasolinerasFiltro = []
        for gasolinera in json.get('ListaEESSPrecio'):
            latitudD = float(gasolinera.get('Latitud').replace(',','.'))
            longitudD = float(gasolinera.get('Longitud (WGS84)').replace(',','.'))
            if (getDistancia(latitudO=latitud,longitudO=longitud,latitudD=latitudD,longitudD=longitudD) < distancia):
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
                pMin = int(periodo.get('periodo')[0:2])
                pMax = int(periodo.get('periodo')[3:])
                if hora > pMin and hora < pMax:
                    pPrecipitacion = periodo.get('value')


            estadoCielo = diaPrediccion.get('estadoCielo')
            for periodo in estadoCielo:
                pMin = int(periodo.get('periodo')[0:2])
                pMax = int(periodo.get('periodo')[3:])
                if hora > pMin and hora < pMax:
                    eCielo = periodo.get('descripcion')
            
            viento = diaPrediccion.get('viento')

            for periodo in viento:
                pMin = int(periodo.get('periodo')[0:2])
                pMax = int(periodo.get('periodo')[3:])
                if hora > pMin and hora < pMax:
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
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if request.query_params.get('fecha'):
            fecha = request.query_params.get('fecha')
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if request.query_params.get('hora'):
            hora = int(request.query_params.get('hora'))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        respuestaAllMunicipios = requests.get(URL_AEMET + "/maestro/municipios",headers={"Content-Type" : "application/json","api_key":API_KEY_AEMET})

        municipioID = getMunicipioID(respuestaAllMunicipios.json(), municipio)

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
        
        #?f=json&where=(provincia%20IN%20(%27SEVILLA%27))&outFields=poblacion,actualizad,fechahora_,carretera
        if request.query_params.get('municipio') is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        municipio = request.query_params.get('municipio')
        respuesta = requests.get(URL_INCIDENCIAS_TRAFICO + "?f=json&where=(poblacion%20IN%20(%27" + municipio + "%27))&outFields=poblacion,actualizad,fechahora_,carretera")#, headers={"Content-Type" : "application/json"})
            
        
        #if request.query_params.get('provincia') is None:
        #    return Response(status=status.HTTP_400_BAD_REQUEST)
            
        #provincia = request.query_params.get('provincia')
		#respuesta = requests.get(URL_INCIDENCIAS_TRAFICO + "?f=json&where=(provincia%20IN%20(%27" + provincia + "%27))&outFields=poblacion,actualizad,fechahora_,carretera")#, headers={"Content-Type" : "application/json"})
            
        
        json = respuesta.json().get('features')
        
        incidenciasTotales = []
        for features in json:
        	incidenciasTotales.append(features)

        return Response(incidenciasTotales,status=status.HTTP_200_OK)
