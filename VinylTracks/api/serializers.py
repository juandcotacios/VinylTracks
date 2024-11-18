from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Producto, Compra, Proveedor

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    proveedor = serializers.PrimaryKeyRelatedField(queryset=Proveedor.objects.all())

    class Meta:
        model = Producto
        fields = '__all__'
        
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email')

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])  # Encriptación de la contraseña
        user.save()
        return user    

class   CompraSerializer(serializers.ModelSerializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    usuario = serializers.ReadOnlyField(source='usuario.username') 
    class Meta:
        model = Compra
        fields = ['id', 'producto', 'usuario','cantidad_vendida', 'fecha_compra']
