from django.contrib import admin
from .models import Proveedor, Producto, Compra
# Register your models here.


admin.site.register(Proveedor)
admin.site.register(Producto)
admin.site.register(Compra)