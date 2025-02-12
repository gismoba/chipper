from django.utils import timezone
from datetime import timedelta
from .models import AuthToken

def create_token(user):
    expiration_date = timezone.now() + timedelta(hours=1)  # Token valid for 1 hour
    token = AuthToken.objects.create(user=user, expires_at=expiration_date)
    return token.token
