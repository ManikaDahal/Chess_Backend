from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
    username_field = 'email'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['username'] = serializers.CharField(required=False)
        self.fields['captcha_hash'] = serializers.CharField(required=False, write_only=True)
        self.fields['captcha_value'] = serializers.CharField(required=False, write_only=True)

    def validate(self, attrs):
        # Captcha is optional for now or can be enforced based on logic
        hashkey = attrs.get('captcha_hash')
        response = attrs.get('captcha_value')
        
        if hashkey and response:
            from captcha.models import CaptchaStore
            try:
                CaptchaStore.objects.get(hashkey=hashkey, response=response.lower()).delete()
            except CaptchaStore.DoesNotExist:
                raise serializers.ValidationError({"captcha": "Invalid or expired captcha"})
        
        if not attrs.get('email') and attrs.get('username'):
            attrs['email'] = attrs.get('username')
        
        if not attrs.get('email'):
            raise serializers.ValidationError("Either email or username is required.")
            
        return super().validate(attrs)
