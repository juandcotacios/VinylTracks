from django.shortcuts import render

# Create your views here.

def comprar(request):
    context = {
        "nombre": "Compras"
    }
    return render(request,"compras/indexCompras.html", context)