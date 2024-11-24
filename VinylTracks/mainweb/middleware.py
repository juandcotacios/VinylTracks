from django.shortcuts import redirect
from django.urls import reverse

class CheckAuthTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        exempt_routes = [
            reverse('mainweb:login'),
            reverse('mainweb:register'),
            reverse('mainweb:index'),  # Permitir acceso a la página principal
            '/static/',  # Archivos estáticos
        ]

        # Excluir API y rutas exentas
        if request.path.startswith('/api/') or request.path in exempt_routes:
            return self.get_response(request)

        # Verifica el token en la sesión
        if not request.session.get("auth_token"):
            return redirect('mainweb:login')

        return self.get_response(request)
