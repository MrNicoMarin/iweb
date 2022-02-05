import json

class UsuarioDto():
    
    def __init__(self, id, name, email, apellidos, imagen, fechaNacimiento, twitterToken):
        self.id = id
        self.name = name
        self.email = email
        self.apellidos = apellidos
        self.imagen = imagen
        self.fechaNacimiento = fechaNacimiento
        self.twitterToken = twitterToken is not None

    def __init__(self, usuario):
        self.id = usuario.id
        self.name = usuario.name
        self.email = usuario.email
        self.apellidos = usuario.apellidos
        self.imagen = usuario.imagen
        self.fechaNacimiento = usuario.fechaNacimiento
        self.twitterToken = usuario.twitterToken is not None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    

    @staticmethod
    def toUsuariosDto(usuarios):
        lista = []
        for u in usuarios:
            lista.append(UsuarioDto(u))
        return lista

    
class UbicacionDto():
    
    def __init__(self, id, latitud, longitud, municipio):
        self.id = id
        self.latitud = latitud
        self.longitud = longitud
        self.municipio = municipio

    def __init__(self,ubicacion):
        self.id = ubicacion.id
        self.latitud = ubicacion.latitud
        self.longitud = ubicacion.longitud
        self.municipio = ubicacion.municipio
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    @staticmethod
    def toUbicacionDto(ubicaciones):
        lista = []
        for u in ubicaciones:
            lista.append(UbicacionDto(u))
        return lista

class VehiculoDto():
    
    def __init__(self, id, usuario, modelo, color, matricula, imagen, plazas):
        self.id = id
        self.usuario = usuario
        self.modelo = modelo
        self.color = color
        self.matricula = matricula
        self.imagen = imagen
        self.plazas = plazas

    def __init__(self,vehiculo):
        self.id = vehiculo.id
        self.usuario = UsuarioDto(vehiculo.usuario)
        self.modelo = vehiculo.modelo
        self.color = vehiculo.color
        self.matricula = vehiculo.matricula
        self.imagen = vehiculo.imagen
        self.plazas = vehiculo.plazas
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    @staticmethod
    def toVehiculoDto(vehiculo):
        lista = []
        for u in vehiculo:
            lista.append(VehiculoDto(u))
        return lista

class TrayectoDto():
    
    def __init__(self, id, origen, paradas, destino, piloto, vehiculo, precio, fechaSalida):
        self.id = id
        self.origen = origen
        self.paradas = paradas
        self.destino = destino
        self.piloto = piloto
        self.vehiculo = vehiculo
        self.precio = precio
        self.fechaSalida = fechaSalida

    def __init__(self,trayectoria):
        self.id = trayectoria.id
        self.origen = UbicacionDto(trayectoria.origen)
        self.paradas = UbicacionDto.toUbicacionDto(trayectoria.paradas.all())
        self.destino = UbicacionDto(trayectoria.destino)
        self.piloto = UsuarioDto(trayectoria.piloto)
        self.vehiculo = VehiculoDto(trayectoria.vehiculo)
        self.precio = trayectoria.precio
        self.fechaSalida = trayectoria.fechaSalida
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    @staticmethod
    def toTrayectoDto(trayectorias):
        lista = []
        for u in trayectorias:
            lista.append(TrayectoDto(u))
        return lista

class ReservaDto():
    def __init__(self, id, trayecto, usuario, fechaReserva):
        self.id = id
        self.trayecto = trayecto
        self.usuario = usuario
        self.fechaReserva = fechaReserva

    def __init__(self, reserva):
        self.id = reserva.id
        self.trayecto = TrayectoDto(reserva.trayecto)
        self.usuario = UsuarioDto(reserva.usuario)
        self.fechaReserva = reserva.fechaReserva
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    @staticmethod
    def toReservaDto(reservas):
        lista = []
        for u in reservas:
            lista.append(ReservaDto(u))
        return lista
    

class GasolineraDto():
    
    def __init__(self,Direccion,Horario,Latitud,Municipio,Longitud,PrecioGA,PrecioGPremium,Precio95,Precio98):
        self.Direccion = Direccion
        self.Horario = Horario
        self.Latitud = Latitud
        self.Municipio = Municipio
        self.Longitud = float(Longitud)
        self.PrecioGA = float(PrecioGA)
        self.PrecioGPremium = float(PrecioGPremium)
        self.Precio95 = float(Precio95)
        self.Precio98 = float(Precio98)
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    @staticmethod
    def toGasolineraDto(gasolineras):
        lista = []
        for u in gasolineras:
            lista.append(GasolineraDto(u))
        return lista

class ComentarioDto():

    def __init__(self,id,creador,usuario,text):
        self.id = id
        self.creador = creador
        self.usuario = usuario
        self.text = text

    def __init__(self, comentario):
        self.id = comentario.id
        self.creador = UsuarioDto(comentario.creador)
        self.usuario = UsuarioDto(comentario.usuario)
        self.text = comentario.text
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    @staticmethod
    def toComentarioDto(comentarios):
        lista = []
        for c in comentarios:
            lista.append(ComentarioDto(c))
        return lista