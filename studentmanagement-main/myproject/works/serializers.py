# classroom/serializers.py
from rest_framework import serializers
from .models import Work, Submission
from teachers.models import Teacher
from myapp.models import StudentRegistration
from cources.models import Course


class WorkSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Work
        fields = ['id', 'teacher', 'course', 'title', 'description', 'work_file', 'created_at']


class SubmissionSerializer(serializers.ModelSerializer):
    work = serializers.PrimaryKeyRelatedField(queryset=Work.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=StudentRegistration.objects.all())

    class Meta:
        model = Submission
        fields = ['id', 'work', 'student', 'answer_file', 'submitted_at', 'status']
        read_only_fields = ['submitted_at', 'status']
