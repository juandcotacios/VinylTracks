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
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User


# Create your views here.

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
