from rest_framework import serializers
from .models import Result

class ResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    subject_name = serializers.CharField(source="subject.subject_name", read_only=True)
    exam_title = serializers.CharField(source="exam.title", read_only=True)

    class Meta:
        model = Result
        fields = ['id', 'student', 'student_name', 'subject', 'subject_name', 'exam', 'exam_title', 'marks', 'remarks']
