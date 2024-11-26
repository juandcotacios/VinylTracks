from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import Producto, Compra, Proveedor
from .serializers import ProductoSerializer, CompraSerializer, ProveedorSerializer, UserSerializer
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F
from rest_framework.views import APIView
from .models import Compra
import plotly.graph_objects as go
from django.http import HttpResponse
from django.utils.timezone import now, timedelta
from django.db.models import Sum, F
from rest_framework.permissions import AllowAny
from django.utils.timezone import now
from datetime import timedelta
from django.http import HttpResponse
from django.db.models import Sum



# Create your views here.

class ComprasPorUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Filtrar las compras realizadas por el usuario autenticado
        compras = Compra.objects.filter(usuario=request.user)
        serializer = CompraSerializer(compras, many=True)
        return Response(serializer.data)
    
    
class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })
    
class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [AllowAny]
    
class ProductoViewSet(viewsets.ModelViewSet):    
 queryset = Producto.objects.all()
 serializer_class = ProductoSerializer
 permission_classes = [AllowAny]

class CompraViewSet(viewsets.ModelViewSet): 
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] 
    def perform_create(self, serializer):

        serializer.save(usuario=self.request.user)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(usuario=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
class CartValidationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        carrito = request.data.get("cart", {})
        errors = []
        for item in carrito:
            producto = Producto.objects.get(id=item["product_id"])
            if producto.cantidad_en_inventario < item["quantity"]:
                errors.append({
                    "product_id": producto.id,
                    "name": producto.nombre,
                    "error": "No hay suficiente inventario"
                })

        if errors:
            return Response({"errors": errors}, status=400)
        return Response({"message": "Carrito válido"}, status=200)

class ViewsWeb(APIView):
    permission_classes = [AllowAny]  # Permitir acceso a usuarios autenticados o no autenticados

    def get(self, request):
        # Recuperar el token de la sesión (si existe)
        auth_token = request.session.get("auth_token", None)

        # Determinar si el usuario está autenticado
        is_authenticated = bool(auth_token)

        # Obtener los productos de la base de datos
        productos = Producto.objects.all()

        # Construir el contexto para la respuesta
        context = {
            "is_authenticated": is_authenticated,
            "productos": productos,
        }

        if is_authenticated:
            # Si el usuario está autenticado, obtener información adicional
            username = request.session.get("username", "Invitado")
            context["username"] = username

        return render(request, "mainweb/indexWebUser.html", context)



# Reporte de ventas totales
class VentasTotalesView(APIView):
    permission_classes = [AllowAny]  # Permite acceso sin autenticación

    def get(self, request):
        total_ventas = Compra.objects.aggregate(total=Sum(F('cantidad_vendida') * F('producto__precio')))
        return Response({"total_ventas": total_ventas['total']})

# Producto más vendido
class ProductoMasVendidoView(APIView):
    permission_classes = [AllowAny]  # Permite acceso sin autenticación

    def get(self, request):
        producto_mas_vendido = Compra.objects.values('producto__nombre') \
            .annotate(total_vendido=Sum('cantidad_vendida')) \
            .order_by('-total_vendido').first()

        if producto_mas_vendido:
            return Response({
                "producto": producto_mas_vendido['producto__nombre'],
                "cantidad_vendida": producto_mas_vendido['total_vendido']
            })
        else:
            return Response({"error": "No se han realizado compras aún."})
        
        # Ventas por fecha


# Ventas por usuario
class VentasPorUsuarioView(APIView):
    permission_classes = [AllowAny]  # Permite acceso sin autenticación

    def get(self, request, usuario_id):
        ventas_usuario = Compra.objects.filter(usuario__id=usuario_id) \
            .aggregate(total=Sum(F('cantidad_vendida') * F('producto__precio')))
        return Response({"usuario_id": usuario_id, "total_ventas": ventas_usuario['total']})
    

def producto_mas_vendido_grafico(request):
    # Obtener los productos más vendidos
    productos = (
        Compra.objects.values('producto__nombre')
        .annotate(total_vendido=Sum('cantidad_vendida'))
        .order_by('-total_vendido')[:10]  # Limitar a los 10 más vendidos
    )

    # Extraer nombres y cantidades para el gráfico
    nombres = [producto['producto__nombre'] for producto in productos]
    cantidades = [producto['total_vendido'] for producto in productos]

    # Crear el gráfico con Plotly
    fig = go.Figure()
    fig.add_trace(go.Bar(x=nombres, y=cantidades, name="Cantidad Vendida"))
    fig.update_layout(
        title="Top 10 Productos Más Vendidos",
        xaxis_title="Producto",
        yaxis_title="Cantidad Vendida",
        template="plotly_white",
    )

    # Renderizar el gráfico como HTML
    html = fig.to_html(full_html=False)
    return HttpResponse(html)

def ventas_por_usuario_grafico(request):
    # Obtener ventas totales agrupadas por usuario
    ventas_usuario = (
        Compra.objects.values('usuario__username')  # Agrupar por nombre de usuario
        .annotate(total_ventas=Sum(F('cantidad_vendida') * F('producto__precio')))  # Calcular ventas totales
        .order_by('-total_ventas')  # Ordenar por ventas totales de mayor a menor
    )

    # Extraer nombres de usuarios y ventas para el gráfico
    usuarios = [venta['usuario__username'] for venta in ventas_usuario]
    totales = [venta['total_ventas'] for venta in ventas_usuario]

    # Crear el gráfico con Plotly
    fig = go.Figure()
    fig.add_trace(go.Bar(x=usuarios, y=totales, name="Ventas Totales"))
    fig.update_layout(
        title="Ventas Totales por Usuario",
        xaxis_title="Usuario",
        yaxis_title="Ventas Totales (en dinero)",
        template="plotly_white",
    )

    # Renderizar el gráfico como HTML
    html = fig.to_html(full_html=False)
    return HttpResponse(html)