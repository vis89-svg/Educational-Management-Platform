# exam/models.py

from django.db import models
from myapp.models import StudentRegistration

class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    duration = models.IntegerField()

    def __str__(self):
        return self.title


class ExamResponse(models.Model):
    student = models.ForeignKey(StudentRegistration, on_delete=models.CASCADE, related_name="exam_responses")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="responses")
    accepted = models.BooleanField(default=False)   

    class Meta:
        unique_together = ("student", "exam")   
