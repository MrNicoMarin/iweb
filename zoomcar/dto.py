import json

class UsuarioDto():
    
    def __init__(self, id, name, email, apellidos, imagen, fechaNacimiento):
        self.id = id
        self.name = name
        self.email = email
        self.apellidos = apellidos
        self.imagen = imagen
        self.fechaNacimiento = fechaNacimiento

    def __init__(self, usuario):
        self.id = usuario.id
        self.name = usuario.name
        self.email = usuario.email
        self.apellidos = usuario.apellidos
        self.imagen = usuario.imagen
        self.fechaNacimiento = usuario.fechaNacimiento

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
    def __init__(self, trayecto, usuario, fechaReserva):
        self.trayecto = trayecto
        self.usuario = usuario
        self.fechaReserva = fechaReserva

    def __init__(self, reserva):
        self.trayecto = reserva.trayecto
        self.usuario = UsuarioDto(reserva.usuario)
        self.fechaReserva = reserva.fechareserva
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    @staticmethod
    def toReservaDto(reservas):
        lista = []
        for u in reservas:
            lista.append(ReservaDto)
        return lista
    

    