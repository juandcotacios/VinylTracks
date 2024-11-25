from django.shortcuts import redirect
from functools import wraps
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.utils.functional import SimpleLazyObject

def token_required(view_func):
    """
    Decorador para verificar si el usuario tiene un token de autenticación en la sesión.
    Sincroniza `request.user` con el usuario autenticado.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Recuperar el token de la sesión
        token_key = request.session.get("auth_token")
        if not token_key:
            # Redirigir al login si no hay token
            return redirect('mainweb:login')

        try:
            # Obtener el token y el usuario asociado
            token = Token.objects.get(key=token_key)
            request.user = token.user  # Sincronizar el usuario con el request
        except Token.DoesNotExist:
            # Redirigir al login si el token no es válido
            return redirect('mainweb:login')

        # Manejar casos en los que `request.user` es un SimpleLazyObject
        if isinstance(request.user, SimpleLazyObject):
            request.user = User.objects.get(pk=request.user.pk)

        # Añadir el token al request para su uso en la vista
        request.auth_token = token_key
        return view_func(request, *args, **kwargs)

    return _wrapped_view
