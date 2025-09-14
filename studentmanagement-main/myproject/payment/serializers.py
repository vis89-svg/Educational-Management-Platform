# payment/serializers.py

from rest_framework import serializers
from .models import ExamPayment
from Exam.models import Exam
from myapp.models import StudentRegistration


class ExamPaymentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=StudentRegistration.objects.all())
    exam = serializers.PrimaryKeyRelatedField(queryset=Exam.objects.all())

    exam_title = serializers.CharField(source="exam.title", read_only=True)
    student_username = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = ExamPayment
        fields = [
            "id",
            "student",
            "student_username",
            "exam",
            "exam_title",
            "method",
            "status",
            "razorpay_order_id",
            "razorpay_payment_id",
            "razorpay_signature",
            "amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "status",  # status is controlled by system/admin/razorpay
            "razorpay_order_id",
            "razorpay_payment_id",
            "razorpay_signature",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        """
        Ensure a student can only pay once for the same exam.
        """
        student = data.get("student")
        exam = data.get("exam")

        if ExamPayment.objects.filter(student=student, exam=exam).exists():
            raise serializers.ValidationError("Payment for this exam already exists.")
        return data
