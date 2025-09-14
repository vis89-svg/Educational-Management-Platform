from rest_framework import serializers
from .models import StudentRegistration
from cources.models import Course

class StudentRegistrationSerializer(serializers.ModelSerializer):
    class_name = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = StudentRegistration
        fields = ['id', 'username', 'name', 'password', 'class_name', 'admission_date', 'age', 'email']
