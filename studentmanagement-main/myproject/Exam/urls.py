from django.urls import path
from .views import ExamListView, ExamAddView, ExamEdit, ExamDelete, ExamView

urlpatterns = [

    path("exams/", ExamListView.as_view(), name="exam-list"),
    path("exams/add/", ExamAddView.as_view(), name="exam-add"),
    path("exams/<int:pk>/edit/", ExamEdit.as_view(), name="exam-edit"),
    path("exams/<int:pk>/delete/", ExamDelete.as_view(), name="exam-delete"),

    path("api/exams/", ExamView.as_view(), name="exam-view"),
]
