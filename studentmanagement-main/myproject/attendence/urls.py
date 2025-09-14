from django.urls import path
from .views import AttendanceMarkView, AttendanceListView

urlpatterns = [
    path("mark/", AttendanceMarkView.as_view(), name="attendance-mark"),
    path("records/", AttendanceListView.as_view(), name="attendance-list"),
]
