import json

class UsuarioDto():
    
    def __init__(self):
        self.id = None
        self.name = None
        self.email = None
        self.apellidos = None

    def __init__(self, usuario):
        self.id = usuario.id
        self.name = usuario.name
        self.email = usuario.email
        self.apellidos = usuario.apellidos

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
    
    def __init__(self):
        self.latitud = None
        self.longitud = None

    def __init__(self,ubicacion):
        self.latitud = ubicacion.latitud
        self.longitud = ubicacion.longitud
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    @staticmethod
    def toUbicacionDto(ubicaciones):
        lista = []
        for u in ubicaciones:
            lista.append(UbicacionDto(u))
        return lista