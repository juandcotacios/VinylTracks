from django.shortcuts import render

# Create your views here.
def gestionar(request):
    context = {
        "nombre": "Inventario"
    }
    return render(request,"inventario/indexWebUser.html", context)