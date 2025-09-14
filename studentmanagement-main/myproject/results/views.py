from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from .models import Result
from .serializers import ResultSerializer
from myapp.models import StudentRegistration
from cources.models import Course, Subject
from Exam.models import Exam
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse

class ResultEntryView(APIView):
    template_name = "results_entry.html"

    def get(self, request):
        courses = Course.objects.all()
        exams = Exam.objects.all()
        students = []
        subjects = []
        selected_class = request.GET.get("class_id")
        selected_exam = request.GET.get("exam_id")

        if selected_class and selected_exam:
            students = StudentRegistration.objects.filter(class_name_id=selected_class)
            subjects = Subject.objects.filter(course_id=selected_class)

        return render(request, self.template_name, {
            "courses": courses,
            "exams": exams,
            "students": students,
            "subjects": subjects,
            "selected_class": selected_class,
            "selected_exam": selected_exam
        })

    def post(self, request):
        class_id = request.POST.get("class_id")
        exam_id = request.POST.get("exam_id")

        students = StudentRegistration.objects.filter(class_name_id=class_id)
        subjects = Subject.objects.filter(course_id=class_id)

        for student in students:
            for subject in subjects:
                key = f"marks_{student.id}_{subject.id}"
                marks = request.POST.get(key)
                if marks:
                    Result.objects.update_or_create(
                        student=student,
                        subject=subject,
                        exam_id=exam_id,
                        defaults={"marks": marks}
                    )

        messages.success(request, "Results saved successfully!")
        return redirect("results-view")


class ResultView(View):
    template_name = "results_view.html"

    def get(self, request):
        classes = Course.objects.all()
        exams = Exam.objects.all()
        selected_class = request.GET.get("class_id")
        selected_exam = request.GET.get("exam_id")
        students = []
        subjects = []
        flat_results = []

        if selected_class and selected_exam:
            students = StudentRegistration.objects.filter(class_name_id=selected_class)
            subjects = Subject.objects.filter(course_id=selected_class)
            exam_id = selected_exam

            # Flatten results for template (list of marks per student)
            for student in students:
                row = {"student": student, "marks": []}
                for subject in subjects:
                    result = Result.objects.filter(
                        student=student, subject=subject, exam_id=exam_id
                    ).first()
                    row["marks"].append(result.marks if result else "-")
                flat_results.append(row)

        return render(request, self.template_name, {
            "classes": classes,
            "exams": exams,
            "students": students,
            "subjects": subjects,
            "flat_results": flat_results,
            "selected_class": selected_class,
            "selected_exam": selected_exam
        })
