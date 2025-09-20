from myapp.models import StudentRegistration
from django.shortcuts import render, redirect, get_object_or_404
from myapp.serializers import StudentRegistrationSerializer
from teachers.models import Teacher
from teachers.serializers import TeacherSerializer
from cources.models import Course
from cources.serializers import CourseSerializer
from django.db import models
from django.utils import timezone
from teachers.models import Teacher
from cources.models import Course


class Work(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="works" , null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="works")
    title = models.CharField(max_length=255)
    description = models.TextField()
    work_file = models.FileField(upload_to="teacher_works/", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} ({self.course.class_name})"


class Submission(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("REVIEWING", "Reviewing"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
    ]

    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(StudentRegistration, on_delete=models.CASCADE, related_name="submissions")
    answer_file = models.FileField(upload_to="student_submissions/", null=True, blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    class Meta:
        unique_together = ("work", "student")  # one submission per student per work

    def __str__(self):
        return f"{self.student.username} - {self.work.title} ({self.status})"
