from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class SignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

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

    def validate(self, attrs):
        if not attrs.get('email') and attrs.get('username'):
            attrs['email'] = attrs.get('username')
        
        if not attrs.get('email'):
            raise serializers.ValidationError("Either email or username is required.")
            
        return super().validate(attrs)
