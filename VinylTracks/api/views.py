from rest_framework import viewsets
from rest_framework.response import Response
from .models import Producto, Compra, Proveedor
from .serializers import ProductoSerializer, CompraSerializer, ProveedorSerializer
# Create your views here.

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer

    def perform_create(self, serializer):
   
        serializer.save()
