from django.contrib.auth import logout
from django.utils import timezone
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si el usuario está autenticado
        if request.user.is_authenticated:
            # Obtener el último acceso desde la sesión
            last_activity = request.session.get('last_activity')
            
            # Si no hay última actividad, establecer la hora actual
            if not last_activity:
                request.session['last_activity'] = timezone.now().isoformat()
            else:
                # Convertir la última actividad a objeto datetime
                last_activity = timezone.datetime.fromisoformat(last_activity)
                
                # Calcular tiempo transcurrido
                time_elapsed = timezone.now() - last_activity
                
                # Si han pasado más de 5 minutos, cerrar sesión
                if time_elapsed.total_seconds() > 300:  # 5 minutos
                    logout(request)
                    # Redirigir a login con mensaje de sesión expirada
                    messages.warning(request, 'Su sesión ha expirado por inactividad.')
                    return redirect('login')
            
            # Actualizar la última actividad en cada request
            request.session['last_activity'] = timezone.now().isoformat()

        response = self.get_response(request)
        return response