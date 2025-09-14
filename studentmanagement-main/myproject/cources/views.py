from django.shortcuts import render, redirect
from django.views import View
from .models import Course
from .serializers import CourseSerializer
from .models import Subject
from .serializers import SubjectSerializer
from django.contrib import messages

class CourseView(View):
    template_name = "courses.html"

    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return render(request, self.template_name, {"courses": serializer.data})

    def post(self, request):
        serializer = CourseSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return redirect("courses")  # redirect to the same page or any named URL
        # If not valid, re-render with errors
        courses = Course.objects.all()
        courses_serializer = CourseSerializer(courses, many=True)
        return render(request, self.template_name, {
            "courses": courses_serializer.data,
            "errors": serializer.errors
        })


class SubjectView(View):
    template_name = "subjects.html"

    def get(self, request):
        subjects = Subject.objects.select_related("course").all()
        courses = Course.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return render(request, self.template_name, {
            "subjects": serializer.data,
            "courses": courses
        })

    def post(self, request):
        subject_names = request.POST.getlist("subject_name")  # <-- fix here
        course_id = request.POST.get("course")

        for name in subject_names:
            name = name.strip()
            if name:
                serializer = SubjectSerializer(data={"subject_name": name, "course": course_id})
                if serializer.is_valid():
                    serializer.save()
                else:
                    subjects = Subject.objects.select_related("course").all()
                    courses = Course.objects.all()
                    return render(request, self.template_name, {
                        "subjects": SubjectSerializer(subjects, many=True).data,
                        "courses": courses,
                        "errors": serializer.errors
                    })

        messages.success(request, "Subjects added successfully!")
        return redirect("subjects")
