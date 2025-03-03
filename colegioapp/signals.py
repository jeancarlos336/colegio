from django.core.cache import cache
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

@receiver(user_logged_in)
def limpiar_cache_al_loguear(sender, request, user, **kwargs):
    cache.clear()  # Borra la caché
    print(f"🚀 Caché limpiada al iniciar sesión: {user.username}")  # Mensaje en la terminal
