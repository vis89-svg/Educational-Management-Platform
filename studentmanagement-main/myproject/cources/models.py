from django.db import models

# Create your models here.

class Course(models.Model):
    class_name = models.CharField(max_length=100)


    def __str__(self):
        return self.class_name
    

class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.subject_name