# payment/models.py

from django.db import models
from myapp.models import StudentRegistration
from Exam.models import Exam

class ExamPayment(models.Model):
    PAYMENT_METHODS = [
        ("cash", "Cash"),
        ("razorpay", "Razorpay"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),   # For cash (admin approved)
        ("success", "Success"),     # For Razorpay
        ("failed", "Failed"),
    ]

    student = models.ForeignKey(StudentRegistration, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    # Razorpay fields
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "exam")

    def __str__(self):
        return f"{self.student.username} - {self.exam.title} - {self.status}"
