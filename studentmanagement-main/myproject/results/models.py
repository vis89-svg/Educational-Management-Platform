from django.db import models
from myapp.models import StudentRegistration
from cources.models import Subject, Course
from Exam.models import Exam

class Result(models.Model):
    student = models.ForeignKey(StudentRegistration, on_delete=models.CASCADE, related_name="results")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="results")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="results")
    marks = models.PositiveIntegerField()
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'exam', 'subject')

    def __str__(self):
        return f"{self.student.username} - {self.subject.subject_name} - {self.marks}"
