from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login  # (left as-is)
from django.shortcuts import get_object_or_404, render ,redirect
from .models import StudentRegistration
from .serializers import StudentRegistrationSerializer
from Exam.models import Exam
from Exam.serializers import ExamSerializer, ExamResponseSerializer
from Exam.models import ExamResponse
from django.contrib import messages
from cources.models import Course
from cources.serializers import CourseSerializer
from datetime import date
import calendar
from attendence.models import Attendance
from attendence.serializers import AttendanceSerializer
from calendar import monthrange
from datetime import date


class StudentRegistrationView(APIView):
    template_name = "student_registration.html"

    def get(self, request):
        courses = Course.objects.all()
        return render(request, self.template_name, {"courses": courses})

    def post(self, request):
        serializer = StudentRegistrationSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Registration successful! Please login now.")
            return redirect("login")

        courses = Course.objects.all()
        return render(request, self.template_name, {"courses": courses, "errors": serializer.errors})

from django.contrib.auth.models import User

class LoginAPIView(APIView):
    template_name = "login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        # 1️⃣ Check Django superuser (default User model)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # set session
            if user.is_superuser:
                request.session['superuser'] = 'admin'
                return redirect("admin_profile")
            # Normal Django user (if any)
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            return redirect("profile")

        # 2️⃣ Check StudentRegistration (custom student)
        try:
            student = StudentRegistration.objects.get(username=username, password=password)
        except StudentRegistration.DoesNotExist:
            return render(request, self.template_name, {"error": "Invalid credentials"})

        # Student login success
        request.session['user_id'] = student.id
        request.session['username'] = student.username
        return redirect("profile")

  # adjust path if needed

class ProfileAPIView(APIView):
    template_name = "profile.html"

    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return render(request, self.template_name, {"error": "Unauthorized"})

        try:
            user = StudentRegistration.objects.get(id=user_id)
        except StudentRegistration.DoesNotExist:
            return render(request, self.template_name, {"error": "User not found"})

        exams = Exam.objects.all()

        # 🔹 Get selected month & year from query params (default = current month)
        today = date.today()
        month = int(request.GET.get("month", today.month))
        year = int(request.GET.get("year", today.year))

        # 🔹 Fetch attendance for that student + month
        attendance_records = Attendance.objects.filter(
            student=user, date__year=year, date__month=month
        ).order_by("date")

        return render(
            request,
            self.template_name,
            {
                "user": user,
                "exams": exams,
                "month": month,
                "year": year,
                "attendance_records": attendance_records,
            },
        )



class EditProfileAPIView(APIView):

    template_name = "edit_profile.html"

    def get_object(self, pk=None):


        if self.request.session.get("superuser") == "admin" and pk is not None:
            return get_object_or_404(StudentRegistration, id=pk)


        user_id = self.request.session.get("user_id")
        if not user_id:
            return None
        return get_object_or_404(StudentRegistration, id=user_id)


    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        profile = self.get_object(pk)

        if not profile:
            return render(request, self.template_name, {"error": "Profile not found"})

        return render(request, self.template_name, {"student": profile})


    def post(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        profile = self.get_object(pk)

        if not profile:
            return render(request, self.template_name, {"error": "Profile not found"})

        serializer = StudentRegistrationSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("admin_profile" if request.session.get("superuser") == "admin" else "profile")

        return render(request, self.template_name, {"student": profile, "errors": serializer.errors})


class DeleteStudentAPIView(APIView):
    template_name = "delete_profile.html"

    def get(self, request, pk):
        student = get_object_or_404(StudentRegistration, pk=pk)
        return render(request, self.template_name, {"student": student})

    def post(self, request, pk):

        student = get_object_or_404(StudentRegistration, pk=pk)
        student.delete()
        messages.success(request, "Student profile deleted successfully.")
        return redirect("admin_profile")




class AdminProfileAPIView(APIView):
    template_name = "admin_profile.html"

    def get(self, request):

        if request.session.get("superuser") != "admin":

            return render(request, self.template_name, {"students": []})


        all_students = StudentRegistration.objects.all()
        return render(request, self.template_name, {"students": all_students})



class ForgotPasswordView(APIView):
    template_name = "forgot_password.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")


        student = StudentRegistration.objects.filter(username=username).first()
        if not student:
            return render(request, self.template_name, {"error": "No account found with this username."})


        if new_password != confirm_password:
            return render(request, self.template_name, {"error": "Passwords do not match."})


        student.password = new_password
        student.save()
        messages.success(request, "Password updated successfully! Please login now.")

        return redirect("login")



class LogoutView(APIView):
    def get(self, request):
        request.session.flush()
        return redirect("login")
