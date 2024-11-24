from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
import requests
from django.contrib.auth.decorators import login_required
from api.models import Producto, Order 
from django.shortcuts import render, redirect, get_object_or_404

API_BASE_URL = "http://127.0.0.1:8000/api/"

# Create your views here.
def viewsweb(request):
    token = request.session.get("auth_token")
    if not token:
        return redirect("mainweb:login")
    
    productos = Producto.objects.all()
    context = {
        "productos": productos
    }
    return render(request, "mainweb/indexWebUser.html", context)

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        response = requests.post(f"{API_BASE_URL}login/", data={"username": username, "password": password})
        if response.status_code == 200:
            token = response.json().get("token")
            request.session["auth_token"] = token
            return redirect("mainweb:user_dashboard")  
        else:
            return render(request, "mainweb/login.html", {"error": "Credenciales inválidas"})
    return render(request, "mainweb/login.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        response = requests.post(f"{API_BASE_URL}register/", data={"username": username, "email": email, "password": password})
        if response.status_code == 201:
            return redirect("mainweb:login")
        else:
            error = response.json()
            return render(request, "mainweb/register.html", {"error": error})
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
        context = {
            "user": user_data,
            "orders": Order.objects.filter(usuario=request.user),
        }
        return render(request, "mainweb/user_dashboard.html", context)
    else:
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
    carrito = request.session.get("cart", {})
    carrito[str(product_id)] = carrito.get(str(product_id), 0) + 1
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
    token = request.session.get("auth_token")
    headers = {"Authorization": f"Token {token}"}
    carrito = request.session.get("cart", {})

    order_data = {"items": []}
    total = 0
    for product_id, cantidad in carrito.items():
        producto = Producto.objects.get(id=product_id)
        total += producto.precio * cantidad
        order_data["items"].append({
            "producto": product_id,
            "cantidad": cantidad,
            "precio_unitario": producto.precio
        })
        producto.cantidad_en_inventario -= cantidad
        producto.save()

    order_data["total"] = total
    requests.post(f"{API_BASE_URL}orders/", json=order_data, headers=headers)
    request.session["cart"] = {}
    return redirect("mainweb:user_dashboard")