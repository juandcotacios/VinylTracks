from django.shortcuts import redirect
from django.urls import reverse

class CheckAuthTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define rutas completas de exclusión usando reverse para evitar conflictos de nombres
        exempt_routes = [
            reverse('mainweb:login'),
            reverse('mainweb:register'),
        ]

        # Excluye las solicitudes que van a la API para no interferir con la lógica de backend
        if request.path.startswith('/api/'):
            return self.get_response(request)

        # Verifica si el usuario tiene un token en la sesión
        if not request.session.get("auth_token"):
            # Permitir el acceso solo si la ruta está en las exentas
            if request.path not in exempt_routes:
                return redirect('mainweb:login')

        # Continúa con la solicitud si cumple las condiciones
        return self.get_response(request)
