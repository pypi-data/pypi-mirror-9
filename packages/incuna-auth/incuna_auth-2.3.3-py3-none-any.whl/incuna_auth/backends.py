from django.contrib.auth.backends import ModelBackend
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    # Django < 1.5
    from django.contrib.auth.models import User


class CustomUserModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        """Allow users to log in with their email as well as username."""
        kw = 'email__iexact' if '@' in username else 'username'
        kwargs = {kw: username}
        try:
            user = User.objects.get(**kwargs)
        except User.DoesNotExist:
            pass
        else:
            if user.check_password(password):
                return user
