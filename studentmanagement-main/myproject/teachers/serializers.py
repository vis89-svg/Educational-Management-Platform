from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Teacher

class TeacherSerializer(serializers.ModelSerializer):
    username   = serializers.CharField(source='user.username', required=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name  = serializers.CharField(source='user.last_name', required=False)
    email      = serializers.EmailField(source='user.email', required=False)
    password   = serializers.CharField(write_only=True, required=True, trim_whitespace=False)

    class Meta:
        model  = Teacher
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'subject']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user_data = validated_data.pop('user', {})
        password  = validated_data.pop('password', None)

        user = User(**user_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()

        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher

    def update(self, instance, validated_data):
        user = instance.user
        user_data = validated_data.pop('user', {})

        for attr, value in user_data.items():
            setattr(user, attr, value)

        password = validated_data.pop('password', None)
        if password and password.strip():
            user.set_password(password)

        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
