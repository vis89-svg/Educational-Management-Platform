from django.db import models
from django.utils import timezone
from cources.models import Course   # import Course model from the other app

class StudentRegistration(models.Model):
    username = models.CharField(max_length=100)
    name = models.CharField(max_length=100, null=True)
    password = models.CharField(max_length=100)
    admission_date = models.DateField(default=timezone.now)
    age = models.IntegerField()
    email = models.EmailField()
    class_name = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="students")


    def __str__(self):
        return self.username
