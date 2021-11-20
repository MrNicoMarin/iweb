from rest_framework import serializers

class UsuarioSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    password = serializers.CharField(required=False)
    name = serializers.CharField()
    email = serializers.CharField()
    apellidos = serializers.CharField(required=False)

class UbicacionSerializer(serializers.Serializer):
    longitud = serializers.FloatField()
    latitud = serializers.FloatField()

class VehiculoSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    