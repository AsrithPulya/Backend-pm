from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    reporting_manager = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'role', 'reporting_manager']
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  # Hashing
        return super().create(validated_data)

class UserSerializerList(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'reporting_manager', 'first_name', 'last_name', 'date_joined', 'email', 'role']
    

