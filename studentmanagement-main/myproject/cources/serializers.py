from rest_framework import serializers
from .models import Course
from .models import Subject


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'class_name']


class SubjectSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.class_name", read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'subject_name', 'course', 'course_name']