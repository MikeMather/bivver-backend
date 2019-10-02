from bcrypt import hashpw, checkpw, gensalt
from .models import User


class UserBackend:
    """
    Custom authenticator to work with our legacy bcrypt password hashes
    """
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        if checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return user
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None