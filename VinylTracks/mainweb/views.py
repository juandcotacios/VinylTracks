from django.shortcuts import render
from api.models import Producto
from django.shortcuts import render

# Create your views here.
def viewsweb(request):
    productos = Producto.objects.all()
    context = {
        "productos": productos
    }
    return render(request,"mainweb/indexWebUser.html", context)

def login_view(request):
    return render(request, "mainweb/login.html")