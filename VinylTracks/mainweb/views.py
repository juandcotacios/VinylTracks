from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
import requests
from django.contrib.auth.decorators import login_required
from api.models import Producto, Order 
from django.shortcuts import render, redirect, get_object_or_404

API_BASE_URL = "http://127.0.0.1:8000/api/"

# Create your views here.
# Vista principal
def viewsweb(request):
    
     
    productos = Producto.objects.all()
    context = {
        "productos": productos
    }
    return render(request, "mainweb/indexWebUser.html", context)

# Vista de inicio de sesión
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Enviar solicitud al endpoint de inicio de sesión
        response = requests.post(
            f"{API_BASE_URL}login/",
            data={"username": username, "password": password},
            allow_redirects=False
        )

        # Manejar la respuesta de la API
        if response.status_code == 200:  # Inicio de sesión exitoso
            token = response.json().get("token")
            request.session["auth_token"] = token
            print(f"Login successful: token={token}")  # Log para depuración
            return redirect("mainweb:index")
        elif response.status_code == 400:  # Credenciales inválidas
            print("Login failed: Invalid credentials")  # Log para depuración
            return render(request, "mainweb/login.html", {"error": "Credenciales inválidas"})
        else:  # Otros errores
            print(f"Login error: {response.status_code} - {response.text}")  # Log para depuración
            return render(request, "mainweb/login.html", {"error": "Error inesperado al intentar iniciar sesión"})

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


@login_required
def user_dashboard(request):
    token = request.session.get("auth_token")
    if not token:
        return redirect("mainweb:login")
    
    # Obtener datos del usuario a través de la API
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(f"{API_BASE_URL}users/me/", headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        orders = Order.objects.filter(usuario=request.user)
        context = {
            "user": user_data,
            "orders": orders,
        }
        print("Dashboard loaded successfully.")  # Log para depuración
        return render(request, "mainweb/user_dashboard.html", context)
    else:
        print(f"Error loading dashboard: {response.status_code} - {response.text}")  # Log para depuración
        return redirect("mainweb:login")
    

def logout_view(request):
    request.session.flush()  # Elimina todos los datos de sesión
    return redirect("mainweb:login")

@login_required
def profile_view(request):
    token = request.session.get("auth_token")
    headers = {"Authorization": f"Token {token}"}
    if request.method == "POST":
        data = {
            "first_name": request.POST.get("first_name"),
            "last_name": request.POST.get("last_name"),
            "birthday": request.POST.get("birthday"),
        }
        response = requests.put(f"{API_BASE_URL}users/me/", data=data, headers=headers)
        if response.status_code == 200:
            return redirect("mainweb:profile")
        else:
            error = response.json().get("error", "Error al actualizar el perfil.")
            return render(request, "mainweb/profile.html", {"error": error})

    response = requests.get(f"{API_BASE_URL}users/me/", headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return render(request, "mainweb/profile.html", {"user": user_data})
    else:
        return redirect("mainweb:login")
    # Vista para añadir productos al carrito
def add_to_cart(request, product_id):
    producto = get_object_or_404(Producto, id=product_id)
    cantidad = int(request.POST.get("cantidad", 1))
    if cantidad > producto.cantidad_en_inventario:
        return redirect("mainweb:product_detail", product_id=product_id)

    carrito = request.session.get("cart", {})
    carrito[str(product_id)] = carrito.get(str(product_id), 0) + cantidad
    request.session["cart"] = carrito
    return redirect("mainweb:cart")

# Vista para mostrar el carrito
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


@login_required
def checkout(request):
    # Obtener el token de la sesión
    token = request.session.get("auth_token")
    if not token:
        # Si no hay token, redirige al login
        return redirect("mainweb:login")

    headers = {"Authorization": f"Token {token}"}
    carrito = request.session.get("cart", {})

    if not carrito:
        # Si el carrito está vacío, redirige al dashboard con un mensaje
        return redirect("mainweb:user_dashboard")

    order_data = {"items": []}
    total = 0
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
    return redirect("mainweb:user_dashboard")


def product_detail(request, product_id):
    producto = get_object_or_404(Producto, id=product_id)
    context = {
        "producto": producto
    }
    return render(request, "mainweb/product_detail.html", context)