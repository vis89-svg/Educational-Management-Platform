from django.shortcuts import render ,redirect,reverse
from .models import Teacher
from .serializers import TeacherSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.contrib import messages
from works.models import Work
from works.serializers import WorkSerializer

class TeacherResgister(APIView):
    template_name = "teacher_register.html"

    def get(self, request):
        teachers = Teacher.objects.all()

        if "text/html" in request.META.get("HTTP_ACCEPT", ""):
            return render(request, self.template_name)

        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TeacherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if "text/html" in request.META.get("HTTP_ACCEPT", ""):
                messages.success(request, "Registration successful. Please log in.")
                return redirect("teacher_login")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if "text/html" in request.META.get("HTTP_ACCEPT", ""):
            return render(request, self.template_name, {"errors": serializer.errors})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Teacher
from works.models import Work, Submission  # Import from works app
from myapp.models import StudentRegistration

class ProfileView(APIView):
    template_name = "teacher_profile.html"

    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            if "text/html" in request.META.get("HTTP_ACCEPT", ""):
                return render(request, self.template_name, {"error": "Not logged in"})
            return Response({"error": "Not logged in"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            teacher = Teacher.objects.get(user__id=user_id)
        except Teacher.DoesNotExist:
            if "text/html" in request.META.get("HTTP_ACCEPT", ""):
                return render(request, self.template_name, {"error": "Teacher profile not found"})
            return Response({"error": "Teacher profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch teacher's works
        works = Work.objects.filter(teacher=teacher).order_by("-created_at")

        # Check if managing a specific work
        work_id = request.GET.get('work_id')
        selected_work = None
        student_submissions = []
        
        if work_id:
            try:
                selected_work = Work.objects.get(id=work_id, teacher=teacher)
                submissions = Submission.objects.filter(work=selected_work)
                students = StudentRegistration.objects.filter(class_name=selected_work.course)
                
                for student in students:
                    submission = submissions.filter(student=student).first()
                    student_submissions.append({
                        "student": student,
                        "submission": submission
                    })
            except Work.DoesNotExist:
                messages.error(request, "Work not found")

        if "text/html" in request.META.get("HTTP_ACCEPT", ""):
            return render(request, self.template_name, {
                "teacher": teacher,
                "works": works,
                "selected_work": selected_work,
                "student_submissions": student_submissions,
            })

        serializer = TeacherSerializer(teacher)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Handle submission status updates from the profile page"""
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "Not logged in")
            return redirect("teacher_login")

        try:
            teacher = Teacher.objects.get(user__id=user_id)
        except Teacher.DoesNotExist:
            messages.error(request, "Teacher profile not found")
            return redirect("teacher_login")

        submission_id = request.POST.get("submission_id")
        action = request.POST.get("action")
        work_id = request.POST.get("work_id")
        
        if not submission_id or not action:
            messages.error(request, "Invalid submission data")
            return redirect("teacher_profile")
            
        try:
            submission = Submission.objects.get(id=submission_id, work__teacher=teacher)
            
            if action == "accept":
                submission.status = "ACCEPTED"
                messages.success(request, f"Accepted submission from {submission.student.username}")
            elif action == "reject":
                submission.status = "REJECTED"
                messages.success(request, f"Rejected submission from {submission.student.username}")
            else:
                messages.error(request, "Invalid action")
                return redirect("teacher_profile")
                
            submission.save()
            
        except Submission.DoesNotExist:
            messages.error(request, "Submission not found")
        
        # Redirect back to profile with work_id to show the same work
        if work_id:
            return redirect(f"{reverse('teacher_profile')}?work_id={work_id}")
        return redirect("teacher_profile")

class EditProfileView(APIView):
    template_name = "teacher_edit_profile.html"

    def get_object(self, pk):
        try:
            return Teacher.objects.get(id=pk)
        except Teacher.DoesNotExist:
            return None

    def get(self, request, **kwargs):
        pk = kwargs.get('pk')
        profile = self.get_object(pk)
        if not profile:
            if "text/html" in request.META.get("HTTP_ACCEPT", ""):
                return render(request, self.template_name, {"error": "Teacher not found"})
            return Response({"error": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND)

        if "text/html" in request.META.get("HTTP_ACCEPT", ""):
            return render(request, self.template_name, {"teacher": profile})

        serializer = TeacherSerializer(profile)
        return Response(serializer.data)

    # ✅ handle POST from HTML form
    def post(self, request, **kwargs):
        return self.put(request, **kwargs)

    def put(self, request, **kwargs):
        pk = kwargs.get('pk')
        profile = self.get_object(pk)
        if not profile:
            return Response({"error": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TeacherSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            if "text/html" in request.META.get("HTTP_ACCEPT", ""):
               messages.success(request, "Profile updated successfully.")
               return redirect("all_teachers")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, **kwargs):
        pk = kwargs.get('pk')
        profile = self.get_object(pk)
        if not profile:
            return Response({"error": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TeacherSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if "text/html" in request.META.get("HTTP_ACCEPT", ""):
                messages.success(request, "Profile updated successfully.")
                return redirect("all_teachers")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AllTeachersView(APIView):
    template_name = "teacher_list.html"

    def get(self, request):
        if request.session.get('superuser') != 'admin':
            if "text/html" in request.META.get("HTTP_ACCEPT", ""):
                return render(request, self.template_name, {"teachers": [], "error": "Unauthorized"})
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        teachers = Teacher.objects.all()
        if "text/html" in request.META.get("HTTP_ACCEPT", ""):
            return render(request, self.template_name, {"teachers": teachers})

        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data)



class LoginView(APIView):
    template_name = "teacher_login.html"

    def get(self, request):
        # render login page
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username') or request.data.get('username')
        password = request.POST.get('password') or request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:  
                request.session['superuser'] = 'admin'
                if "text/html" in request.META.get("HTTP_ACCEPT", ""):
                    return redirect("all_teachers")
                return Response({"message": "Admin login successful"}, status=status.HTTP_200_OK)

            # normal teacher
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            if "text/html" in request.META.get("HTTP_ACCEPT", ""):
                return redirect("teacher_profile")
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)

        if "text/html" in request.META.get("HTTP_ACCEPT", ""):
            return render(request, self.template_name, {"error": "Invalid credentials"})
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class DeleteProfileView(APIView):
    template_name = "delete_confirm.html"

    def get(self, request, pk):
        try:
            teacher = Teacher.objects.get(id=pk)
        except Teacher.DoesNotExist:
            return render(request, self.template_name, {"error": "Teacher not found"})
        return render(request, self.template_name, {"teacher": teacher})

    def post(self, request, pk):
        try:
            profile = Teacher.objects.get(id=pk)
        except Teacher.DoesNotExist:
            return render(request, self.template_name, {"error": "Teacher not found"})

        profile.delete()
        messages.success(request, "Teacher profile deleted successfully.")
        return redirect("all_teachers")   # ✅ Redirect to teachers list after delete



