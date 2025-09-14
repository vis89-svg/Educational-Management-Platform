from django.urls import path
from .views import CourseView
from .views import SubjectView

urlpatterns = [
    path("courses/", CourseView.as_view(), name="courses"),
    path("subjects/", SubjectView.as_view(), name="subjects"),
]
