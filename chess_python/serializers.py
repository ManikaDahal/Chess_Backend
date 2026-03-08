from rest_framework import serializers

#Signup
class  SignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()


#Forgot Password 
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)

    def validate(self, data):
        if not data.get('email') and not data.get('phone'):
            raise serializers.ValidationError("Email or phone is required")
        return data
    

#Verify OTP
class VerifyOTPSerializer(serializers.Serializer):
     email = serializers.EmailField(required=False)
     phone = serializers.CharField(required=False)
     otp = serializers.CharField()


#Reset Password
class ResetPasswordSerializer(serializers.Serializer):
     email = serializers.EmailField(required=False)
     phone = serializers.CharField(required=False)
     otp = serializers.CharField()
     new_password=serializers.CharField()

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class FCMTokenSerializer(serializers.Serializer):
    token = serializers.CharField()

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make 'email' field optional to support older clients sending 'username'
        self.fields['email'].required = False
        # Add 'username' field as an optional fallback
        self.fields['username'] = serializers.CharField(required=False)

    def validate(self, attrs):
        # Provide fallback: if 'email' isn't provided, use the value from 'username'
        if not attrs.get('email') and attrs.get('username'):
            attrs['email'] = attrs.get('username')
        
        if not attrs.get('email'):
            raise serializers.ValidationError("Either email or username is required.")
            
        return super().validate(attrs)
