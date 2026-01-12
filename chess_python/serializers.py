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
