from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        identifier = (
            username or 
            kwargs.get('email') or 
            kwargs.get('username') or 
            kwargs.get(UserModel.USERNAME_FIELD)
        )
        
        if identifier:
            users = UserModel.objects.filter(email=identifier)
            for user in users:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            
            try:
                user = UserModel.objects.get(username=identifier)
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            except UserModel.DoesNotExist:
                pass
        
        return None
