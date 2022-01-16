from rest_framework import serializers

from zoomcar.dto import GasolineraDto, UbicacionDto, UsuarioDto, VehiculoDto, TrayectoDto

class UsuarioSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False)
    password = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    apellidos = serializers.CharField(required=False)
    imagen = serializers.CharField(max_length=100,required=False)
    fechaNacimiento = serializers.DateField(required=False)

    def create(self, validated_data):
        return UsuarioDto(**validated_data)

class UbicacionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    longitud = serializers.FloatField(required=False)
    latitud = serializers.FloatField(required=False)
    municipio = serializers.CharField(max_length=50, required=False)

    def create(self, validated_data):
        return UbicacionDto(**validated_data)

class VehiculoSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    usuario = UsuarioSerializer(required=False)
    modelo = serializers.CharField(max_length=50, required=False)
    color = serializers.CharField(max_length=20, required=False)
    matricula = serializers.CharField(max_length=10, required=False)
    imagen = serializers.CharField(max_length=100, required=False)
    plazas = serializers.IntegerField(required=False)

    def create(self, validated_data):
        return VehiculoDto(**validated_data)

class TrayectoSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    paradas = UbicacionSerializer(required=False,many=True)
    origen = UbicacionSerializer(required=False)
    destino = UbicacionSerializer(required=False)
    piloto = UsuarioSerializer(required=False)
    vehiculo = VehiculoSerializer(required=False)
    precio = serializers.DecimalField(decimal_places=2, max_digits=5,required=False)
    fechaSalida = serializers.DateTimeField(required=False)

    def create(self, validated_data):
        return TrayectoDto(**validated_data)

class ReservaSerializer(serializers.Serializer):
    trayecto = TrayectoSerializer()
    usuario = UsuarioSerializer()
    fechaReserva = serializers.DateTimeField()

class GasolineraSerializer(serializers.Serializer):

    Direccion = serializers.CharField(source="Dirección",required=False)
    Horario = serializers.CharField(required=False)
    Latitud = serializers.CharField(required=False)
    Municipio = serializers.CharField(required=False)
    Longitud = serializers.CharField(source="Longitud (WGS84)",required=False)
    PrecioGA = serializers.CharField(source="Precio Gasoleo A",required=False)
    PrecioGPremium = serializers.CharField(source="Precio Gasoleo Premium",required=False)
    Precio95 = serializers.CharField(source="Precio Gasolina 95 E5",required=False)
    Precio98 = serializers.CharField(source="Precio Gasolina 98 E5",required=False)

    def create(self, validated_data):
        return GasolineraDto(**validated_data)

