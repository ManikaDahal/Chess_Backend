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
            print(f"DEBUG BACKEND: Checking Email matches for {identifier}")
            # Use __iexact for case-insensitive email login
            users = UserModel.objects.filter(email__iexact=identifier)
            for user in users:
                if user.check_password(password) and self.user_can_authenticate(user):
                    print(f"DEBUG BACKEND: Authenticated via Email: {user.username}")
                    return user
            
            print(f"DEBUG BACKEND: Checking Username matches for {identifier}")
            try:
                # Use __iexact for case-insensitive username login as well (common practice)
                user = UserModel.objects.get(username__iexact=identifier)
                if user.check_password(password) and self.user_can_authenticate(user):
                    print(f"DEBUG BACKEND: Authenticated via Username: {user.username}")
                    return user
            except UserModel.DoesNotExist:
                print(f"DEBUG BACKEND: User not found: {identifier}")
                pass
        
        return None
