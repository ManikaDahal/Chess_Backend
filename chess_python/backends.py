from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        # Determine the identifier (it could be passed as 'username' or the custom USERNAME_FIELD 'email')
        identifier = username or kwargs.get(UserModel.USERNAME_FIELD) or kwargs.get('username')
        
        if identifier:
            # Try to find the user by email first
            try:
                user = UserModel.objects.get(email=identifier)
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            except UserModel.DoesNotExist:
                # If not found by email, try by username
                try:
                    user = UserModel.objects.get(username=identifier)
                    if user.check_password(password) and self.user_can_authenticate(user):
                        return user
                except UserModel.DoesNotExist:
                    pass
        
        return None
