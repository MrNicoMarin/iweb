from rest_framework import serializers

class UsuarioSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    password = serializers.CharField()
    name = serializers.CharField()
    email = serializers.CharField()
    apellidos = serializers.CharField()

class UbicacionSerializer(serializers.Serializer):
    longitud = serializers.FloatField()
    latitud = serializers.FloatField()

class VehiculoSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    