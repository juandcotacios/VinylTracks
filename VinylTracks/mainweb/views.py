from django.shortcuts import render

# Create your views here.
def viewsweb(request):
    context = {
        "nombre": "Proveedores"
    }
    return render(request,"proveedores/indexProveedores.html", context)