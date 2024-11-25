from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Producto, Compra, Proveedor, Order, OrderItem

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    proveedor = serializers.PrimaryKeyRelatedField(queryset=Proveedor.objects.all())
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = '__all__'
        
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email')
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado.")
        return value

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])  # Encriptación de la contraseña
        user.save()
        return user    

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
        
class CompraSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    usuario = serializers.ReadOnlyField(source="usuario.username")

    class Meta:
        model = Compra
        fields = ['id', 'producto', 'usuario', 'cantidad_vendida', 'fecha_compra']


class OrderItemSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)  

    class Meta:
        model = OrderItem
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    usuario = serializers.ReadOnlyField(source="usuario.username")  

    class Meta:
        model = Order
        fields = ['id', 'usuario', 'items', 'total', 'fecha_pedido']
