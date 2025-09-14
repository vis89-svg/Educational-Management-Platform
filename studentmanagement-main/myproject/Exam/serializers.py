from rest_framework import serializers
from .models import Exam, ExamResponse
from myapp.models import StudentRegistration


class ExamSerializer(serializers.ModelSerializer):
    accepted = serializers.SerializerMethodField()   # status for logged-in student
    accepted_students = serializers.SerializerMethodField()
    rejected_students = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            'id', 'title', 'description', 'date', 'duration',
            'accepted', 'accepted_students', 'rejected_students'
        ]

    def get_accepted(self, obj):
        # logged in part 
        request = self.context.get("request")
        if request and request.session.get("user_id"):
            student_id = request.session.get("user_id")
            try:
                response = ExamResponse.objects.get(student_id=student_id, exam=obj)
                return response.accepted
            except ExamResponse.DoesNotExist:
                return None
        return None

    def get_accepted_students(self, obj):
        # id accepted , then responce part , 
        responses = ExamResponse.objects.filter(exam=obj, accepted=True).select_related("student")
        return [
            {
                "id": r.student.id,
                "username": r.student.username,
                "email": r.student.email,
            }
            for r in responses
        ]

    def get_rejected_students(self, obj):
      
        responses = ExamResponse.objects.filter(exam=obj, accepted=False).select_related("student")
        return [
            {
                "id": r.student.id,
                "username": r.student.username,
                "email": r.student.email,
            }
            for r in responses
        ]

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be a positive number.")
        return value


class ExamResponseSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = ExamResponse
        fields = ['id', 'student', 'exam', 'accepted']
