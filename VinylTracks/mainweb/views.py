from django.shortcuts import render

# Create your views here.
def viewsweb(request):
    context = {
        "nombre": "mainweb"
    }
    return render(request,"mainweb/indexWebUser.html", context)