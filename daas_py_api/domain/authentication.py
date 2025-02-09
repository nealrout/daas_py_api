from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.conf import settings

class CustomBackend(BaseBackend):
    """Custom authentication backend to use hardcoded credentials from settings.py"""

    def authenticate(self, request, username=None, password=None):
        if username == settings.CUSTOM_AUTH_USERNAME and password == settings.CUSTOM_AUTH_PASSWORD:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)  # Hash password if creating user
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
