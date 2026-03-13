from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.signals import user_login_failed
from axes.handlers.database import AxesDatabaseHandler

class SignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    captcha_hash = serializers.CharField(write_only=True)
    captcha_value = serializers.CharField(write_only=True)

    def validate(self, attrs):
        from captcha.models import CaptchaStore
        hashkey = attrs.get('captcha_hash')
        response = attrs.get('captcha_value')
        
        # Verify captcha
        try:
            CaptchaStore.objects.get(hashkey=hashkey, response=response.lower()).delete()
        except CaptchaStore.DoesNotExist:
            raise serializers.ValidationError({"captcha": "Invalid or expired captcha"})
            
        return attrs

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)

    def validate(self, data):
        if not data.get('email') and not data.get('phone'):
            raise serializers.ValidationError("Email or phone is required")
        return data

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    otp = serializers.CharField()

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    otp = serializers.CharField()
    new_password = serializers.CharField()

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'username'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'] = serializers.CharField(required=False)
        self.fields['email'] = serializers.EmailField(required=False)
        self.fields['captcha_hash'] = serializers.CharField(required=False, write_only=True)
        self.fields['captcha_value'] = serializers.CharField(required=False, write_only=True)

    def validate(self, attrs):
        # Captcha logic
        hashkey = attrs.get('captcha_hash')
        response = attrs.get('captcha_value')
        if hashkey and response:
            from captcha.models import CaptchaStore
            try:
                CaptchaStore.objects.get(hashkey=hashkey, response=response.lower()).delete()
            except CaptchaStore.DoesNotExist:
                raise serializers.ValidationError({"captcha": "Invalid or expired captcha"})
        
        # Robust username/email mapping
        username = attrs.get('username') or attrs.get('email')
        if not username:
             raise serializers.ValidationError("Either email or username is required.")
        
        attrs['username'] = username # Ensure the field SimpleJWT looks for is populated
            
        # NUCLEAR OPTION: Manually check for Axes lockout
        request = self.context.get('request')
        credentials = {'username': username}
        
        print(f"DIAGNOSTIC SERIALIZER: Checking lockout for {username}")
        
        if AxesDatabaseHandler().is_locked(request, credentials):
            print(f"DIAGNOSTIC SERIALIZER: LOCKED OUT {username}")
            raise exceptions.PermissionDenied("Account locked out due to too many failed attempts. Please try again later.")

        try:
            print(f"DIAGNOSTIC SERIALIZER: Calling authenticate for {username}")
            return super().validate(attrs)
        except Exception as e:
            print(f"DIAGNOSTIC SERIALIZER: Auth failed for {username}. Error: {str(e)}")
            # Manually fire signal for Axes
            user_login_failed.send(
                sender=self.__class__,
                credentials={'username': username, 'password': '[CLEANSED]'},
                request=request
            )
            raise e
