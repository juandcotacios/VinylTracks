from django.shortcuts import redirect
from django.urls import reverse

class CheckAuthTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Definir rutas que no requieren autenticación
        exempt_routes = [
            reverse('mainweb:login'),
            reverse('mainweb:register'),
            reverse('mainweb:index'),  # Página principal accesible para todos
        ]

        # Permitir rutas estáticas
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)

        # Permitir API (si quieres que la autenticación sea gestionada por la API directamente)
        if request.path.startswith('/api/'):
            return self.get_response(request)

        # Si la ruta está en las rutas exentas, permitir el acceso
        if request.path in exempt_routes:
            return self.get_response(request)

        # Verificar si el token existe en la sesión
        if not request.session.get("auth_token"):
            # Si no hay token, redirigir al login
            return redirect('mainweb:login')

        # Si todo está bien, continuar con la solicitud
        return self.get_response(request)
