from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
import requests
from django.contrib.auth.decorators import login_required
from api.models import Producto, Order 
from django.shortcuts import render, redirect, get_object_or_404
from .utils import token_required 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash

API_BASE_URL = "http://127.0.0.1:8000/api/"

# Create your views here.
# Vista principal
def viewsweb(request):
    productos = Producto.objects.all()

    # Agregar información del usuario al contexto
    context = {
        "productos": productos,
        "is_authenticated": request.session.get("auth_token") is not None,
        "username": request.session.get("username", None),
    }

    return render(request, "mainweb/indexWebUser.html", context)

# Vista de inicio de sesión
# Vista de inicio de sesión
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            # Enviar solicitud al endpoint de inicio de sesión
            response = requests.post(
                f"{API_BASE_URL}login/",
                data={"username": username, "password": password},
                allow_redirects=False
            )

            # Manejar la respuesta de la API
            if response.status_code == 200:  # Inicio de sesión exitoso
                token = response.json().get("token")

                # Verificar y obtener detalles del usuario desde el endpoint de usuario
                user_response = requests.get(
                    f"{API_BASE_URL}users/me/",
                    headers={"Authorization": f"Token {token}"}
                )

                if user_response.status_code == 200:  # Detalles del usuario obtenidos con éxito
                    user_data = user_response.json()
                    username = user_data.get("username")  # Obtener el nombre de usuario desde la API

                    # Almacenar el token y el nombre del usuario en la sesión
                    request.session["auth_token"] = token
                    request.session["username"] = username

                    print(f"Login successful: token={token}, username={username}")  # Log para depuración
                    return redirect("mainweb:index")  # Redirige al usuario a la página principal

                else:
                    # Error al obtener los datos del usuario
                    print(f"Error fetching user details: {user_response.status_code} - {user_response.text}")
                    return render(request, "mainweb/login.html", {"error": "Error al obtener los datos del usuario. Intente nuevamente."})

            elif response.status_code == 400:  # Credenciales inválidas
                print("Login failed: Invalid credentials")  # Log para depuración
                return render(request, "mainweb/login.html", {"error": "Credenciales inválidas"})

            else:  # Otros errores
                print(f"Login error: {response.status_code} - {response.text}")  # Log para depuración
                return render(request, "mainweb/login.html", {"error": "Error inesperado al intentar iniciar sesión"})

        except requests.RequestException as e:
            # Manejo de errores de conexión o red
            print(f"Login exception: {str(e)}")  # Log para depuración
            return render(request, "mainweb/login.html", {"error": "Error al conectar con el servidor. Intente nuevamente."})

    # Renderizar la página de inicio de sesión para solicitudes GET
    return render(request, "mainweb/login.html")





def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Enviar solicitud al endpoint de registro
        response = requests.post(
            f"{API_BASE_URL}register/",
            data={"username": username, "email": email, "password": password},
            allow_redirects=False
        )

        # Manejar la respuesta de la API
        if response.status_code == 201:  # Registro exitoso
            return redirect("mainweb:login")
        elif response.status_code == 400:  # Error en los datos
            error = response.json()  # Extraer detalles del error
            return render(request, "mainweb/register.html", {"error": error})
        else:  # Otros errores
            return render(request, "mainweb/register.html", {"error": "Error inesperado al intentar registrar"})
    
    # Renderizar la página de registro para solicitudes GET
    return render(request, "mainweb/register.html")

@token_required
def user_dashboard(request):
    headers = {"Authorization": f"Token {request.auth_token}"}

    # Obtener datos del usuario desde la API
    response = requests.get(f"{API_BASE_URL}users/me/", headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        # Filtrar pedidos por el usuario autenticado
        orders = Order.objects.filter(usuario=request.user).prefetch_related('items__producto')


        context = {
            "user": user_data,
            "orders": orders,
        }
        return render(request, "mainweb/user_dashboard.html", context)
    else:
        # Redirigir al login si hay un error en la API
        return redirect("mainweb:login")
    

def logout_view(request):
    # Elimina únicamente los datos relacionados con la sesión del usuario
    if "auth_token" in request.session:
        del request.session["auth_token"]  # Eliminar el token de autenticación
    if "username" in request.session:
        del request.session["username"]  # Eliminar el nombre de usuario
    if "cart" in request.session:
        del request.session["cart"]  # Vaciar el carrito si está presente

    # Limpiar toda la sesión (opcional)
    request.session.flush()

    # Redirigir al usuario a la página principal no autenticada
    return redirect("mainweb:index")



@token_required
def profile_view(request):
    headers = {"Authorization": f"Token {request.auth_token}"}
    user = request.user

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Validaciones para el nombre de usuario
        if username and username != user.username:
            if User.objects.filter(username=username).exists():
                return render(request, "mainweb/profile.html", {"user": user, "error": "El nombre de usuario ya está en uso."})
            user.username = username

        # Validaciones para el correo electrónico
        if email and email != user.email:
            if User.objects.filter(email=email).exists():
                return render(request, "mainweb/profile.html", {"user": user, "error": "El correo electrónico ya está en uso."})
            user.email = email

        # Cambiar contraseña si se proporciona
        if password:
            user.set_password(password)
            update_session_auth_hash(request, user)  # Mantiene la sesión activa tras el cambio de contraseña.

        user.save()
        return render(request, "mainweb/profile.html", {"user": user, "success": "Perfil actualizado con éxito."})

    # Si es una solicitud GET, mostrar la información del usuario.
    return render(request, "mainweb/profile.html", {"user": user})



@token_required    
def add_to_cart(request, product_id):
    # Si el usuario está autenticado, proceder con la lógica de agregar al carrito
    producto = get_object_or_404(Producto, id=product_id)
    cantidad = int(request.POST.get("cantidad", 1))

    # Verificar si hay suficiente inventario
    if cantidad > producto.cantidad_en_inventario:
        return redirect("mainweb:product_detail", product_id=product_id)

    # Obtener el carrito de la sesión o inicializarlo si no existe
    carrito = request.session.get("cart", {})
    carrito[str(product_id)] = carrito.get(str(product_id), 0) + cantidad

    # Guardar el carrito actualizado en la sesión
    request.session["cart"] = carrito

    # Redirigir al carrito después de agregar el producto
    return redirect("mainweb:cart")

@token_required
def remove_from_cart(request, product_id):
    # Obtener el carrito actual de la sesión
    carrito = request.session.get("cart", {})
    
    # Verificar si el producto está en el carrito
    if str(product_id) in carrito:
        del carrito[str(product_id)]  # Eliminar el producto del carrito
    
    # Guardar el carrito actualizado en la sesión
    request.session["cart"] = carrito
    
    # Redirigir al carrito para mostrar los cambios
    return redirect("mainweb:cart")


# Vista para mostrar el carrito
@token_required
def view_cart(request):
    carrito = request.session.get("cart", {})
    productos_en_carrito = []
    total = 0
    for product_id, cantidad in carrito.items():
        producto = Producto.objects.get(id=product_id)
        productos_en_carrito.append({
            "producto": producto,
            "cantidad": cantidad,
            "subtotal": producto.precio * cantidad
        })
        total += producto.precio * cantidad

    context = {
        "productos_en_carrito": productos_en_carrito,
        "total": total,
    }
    return render(request, "mainweb/cart.html", context)

# Vista para procesar el checkout

@token_required
def checkout(request):
    # Obtener el carrito desde la sesión
    carrito = request.session.get("cart", {})

    # Verificar si el carrito está vacío
    if not carrito:
        # Redirigir al dashboard si no hay productos en el carrito
        return redirect("mainweb:user_dashboard")

    headers = {"Authorization": f"Token {request.auth_token}"}
    order_data = {"items": []}
    total = 0

    # Crear los datos del pedido basados en el carrito
    for product_id, cantidad in carrito.items():
        producto = Producto.objects.get(id=product_id)
        total += float(producto.precio) * cantidad  # Convertir Decimal a float
        order_data["items"].append({
            "producto": product_id,
            "cantidad": cantidad,
            "precio_unitario": float(producto.precio)  # Convertir Decimal a float
        })
        producto.cantidad_en_inventario -= cantidad
        producto.save()

    order_data["total"] = float(total)  # Convertir Decimal a float

    # Enviar la solicitud al endpoint de la API
    response = requests.post(f"{API_BASE_URL}orders/", json=order_data, headers=headers)
    if response.status_code != 201:
        print(f"Error al crear el pedido: {response.status_code} - {response.text}")

    # Vaciar el carrito después de la compra
    request.session["cart"] = {}

    # Redirigir al dashboard del usuario después del checkout
    return redirect("mainweb:user_dashboard")



def product_detail(request, product_id):
    producto = get_object_or_404(Producto, id=product_id)
    context = {
        "producto": producto
    }
    return render(request, "mainweb/product_detail.html", context)