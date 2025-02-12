from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from .models import AuthToken

class TokenAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.session.get('auth_token')
        if token:
            try:
                auth_token = AuthToken.objects.get(token=token)
                if auth_token.is_expired():
                    auth_token.delete()
                    request.session.pop('auth_token', None)
                    logout(request)
            except AuthToken.DoesNotExist:
                request.session.pop('auth_token', None)
                logout(request)
