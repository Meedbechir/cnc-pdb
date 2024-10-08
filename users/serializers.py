from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import get_user_model

class SignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        # Ensure passwords match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        
        # Check if username exists
        if not attrs.get('username'):
            raise serializers.ValidationError({"username": "Le nom d'utilisateur est requis."})
        
        return attrs

    def create(self, validated_data):
        # Remove password2 before saving
        validated_data.pop('password2')
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        User = get_user_model() 
        try:
            user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Email ou mot de passe invalide"})

        if not user.check_password(attrs['password']):
            raise serializers.ValidationError({"password": "Email ou mot de passe invalide"})
        
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser  
        fields = ['id', 'username', 'email'] 