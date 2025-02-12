import threading
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser

_thread_locals = threading.local()

def get_current_user():
    user = getattr(_thread_locals, 'user', None)
    if user and isinstance(user, AnonymousUser):
        return None
    return user

class CurrentUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None) or AnonymousUser()
