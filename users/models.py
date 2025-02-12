import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from PIL import Image

ROLE_CHOICES = [
    ("customer", "Customer"),
    ("superuser", "Super User"),
    ("url", "URL Maker"),
    ("artist", "Artist"),
    ("administrator", "Administrator"),
]


class CustomUser(AbstractUser):
    role = models.CharField(
        "Role", choices=ROLE_CHOICES, max_length=50, null=True, blank=True
    )
    image = models.ImageField("Image", upload_to="users/images", null=True, blank=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        if self.username:
            return self.username
        else:
            return self.email

    def save(self, *args, **kwargs):
        super(CustomUser, self).save()
        """reduce image size before upload to server"""
        if self.image:
            basewidth = 350
            img = Image.open(self.image)
            wpercent = basewidth / float(img.size[0])
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            img.save(self.image.path)

    @property
    def is_last_login_updated(self):
        if self.last_login is not None:
            return self.last_login > timezone.now() - timezone.timedelta(seconds=1)
        return False


class AuthToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return self.user.username
