from django.urls import path
from .views import (
    WorkCreateView,
    WorkListTeacherView,
    WorkDetailTeacherView,
    WorkListStudentView,
    SubmissionCreateView,
)

# works/urls.py
urlpatterns = [
    path("teacher/create/", WorkCreateView.as_view(), name="teacher_create_work"),
    path("teacher/", WorkListTeacherView.as_view(), name="teacher_work_list"),
    path("teacher/<int:pk>/", WorkDetailTeacherView.as_view(), name="teacher_work_detail"),

    path("student/", WorkListStudentView.as_view(), name="student_work_list"),
    path("student/<int:work_id>/submit/", SubmissionCreateView.as_view(), name="student_submit_work"),
]

