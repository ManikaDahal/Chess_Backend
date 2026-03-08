from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        # Determine the identifier. It could be in 'username', 'email', or 
        # the model's USERNAME_FIELD keyword argument.
        identifier = (
            username or 
            kwargs.get('email') or 
            kwargs.get('username') or 
            kwargs.get(UserModel.USERNAME_FIELD)
        )
        
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
