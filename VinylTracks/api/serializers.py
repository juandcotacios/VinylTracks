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

class   CompraSerializer(serializers.ModelSerializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())

    class Meta:
        model = Compra
        fields = ['id', 'producto', 'cantidad_vendida', 'fecha_venta']
