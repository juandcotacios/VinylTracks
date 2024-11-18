from django.shortcuts import render

# Create your views here.
def gestionar(request):
    context = {
        "nombre": "mainweb"
    }
    return render(request,"mainweb/indexWebUser.html", context)