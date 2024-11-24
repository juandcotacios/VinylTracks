from django.contrib.auth.models import User 
from django.db import models

# Create your models here.
class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)
    contacto = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    artista = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_en_inventario = models.IntegerField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="productos")
    imagen = models.ImageField(upload_to='productos_imagenes/', null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.artista}"

class Compra(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="compras")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ventas")  
    cantidad_vendida = models.IntegerField()
    fecha_compra = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.producto.cantidad_en_inventario -= self.cantidad_vendida
        self.producto.save()
        super().save(*args, **kwargs)
# Modelo Order
class Order(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Pedido #{self.id} - Usuario: {self.usuario.username}"

# Modelo OrderItem
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.producto.cantidad_en_inventario < self.cantidad:
            raise ValueError("No hay suficiente inventario para completar este pedido.")
        self.producto.cantidad_en_inventario -= self.cantidad
        self.producto.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Pedido #{self.order.id}"