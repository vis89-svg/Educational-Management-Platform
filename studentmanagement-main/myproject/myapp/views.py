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
from payment.models import ExamPayment
from works.models import Work, Submission   # 👈 just import
from works.serializers import WorkSerializer, SubmissionSerializer
def landing_page(request):
    return render(request, "landingpage.html")
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

from django.utils.timezone import now



class ProfileAPIView(APIView):
    template_name = "profile.html"
    
    def get(self, request):
        # ✅ Get logged-in student from session
        user_id = request.session.get('user_id')
        if not user_id:
            return render(request, self.template_name, {"error": "Unauthorized"})
        
        try:
            user = StudentRegistration.objects.get(id=user_id)
        except StudentRegistration.DoesNotExist:
            return render(request, self.template_name, {"error": "User not found"})
        
        # 🔹 Exams
        exams = Exam.objects.all()
        today = now().date()
        recent_exams = Exam.objects.filter(date__gte=today).order_by("date")[:5]
        
        # 🔹 Get selected month & year (default = current) - FIXED TO MATCH
        month = int(request.GET.get("month", today.month))
        year = int(request.GET.get("year", today.year))
        
        # 🔹 Attendance records - FIXED TO MATCH
        attendance_records = Attendance.objects.filter(
            student=user, date__year=year, date__month=month
        ).order_by("date")
        
        # 🔹 Payments
        payments = ExamPayment.objects.filter(student=user).order_by("-created_at")
        
        # 🔹 Works & Submissions
        works = Work.objects.filter(course=user.class_name)
        submissions = Submission.objects.filter(student=user)
        submission_map = {s.work.id: s for s in submissions}
        
        # Preprocess works for template
        works_with_submissions = []
        for work in works:
            submission = submission_map.get(work.id)  # None if not submitted
            works_with_submissions.append({
                "work": work,
                "submission": submission
            })
        
        # ✅ Render with correct request argument - FIXED TO MATCH
        return render(request, self.template_name, {
            "user": user,
            "exams": exams,
            "recent_exams": recent_exams,
            "month": month,  # ADDED TO MATCH
            "year": year,    # ADDED TO MATCH
            "attendance_records": attendance_records,
            "payments": payments,
            "works_with_submissions": works_with_submissions
        })


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

        courses = Course.objects.all()
        return render(
            request,
            self.template_name,
            {"student": profile, "courses": courses},
        )

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

        courses = Course.objects.all()
        return render(
            request,
            self.template_name,
            {"student": profile, "errors": serializer.errors, "courses": courses},
        )



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



from django.db.models import Q

class AdminProfileAPIView(APIView):
    template_name = "admin_profile.html"

    def get(self, request):
        if request.session.get("superuser") != "admin":
            return render(request, self.template_name, {"students": []})

        query = request.GET.get("q", "")
        all_students = StudentRegistration.objects.all()

        if query:
            all_students = all_students.filter(
                Q(name__icontains=query) |
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(class_name__class_name__icontains=query)  # ✅ foreign key lookup
            )

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
