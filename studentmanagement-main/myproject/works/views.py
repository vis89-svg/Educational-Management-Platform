from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib import messages
from rest_framework.views import APIView
from .models import Work, Submission
from myapp.models import StudentRegistration
from cources.models import Course
from teachers.models import Teacher

# ----------------------------
# 1. Teacher: Create Work
# ----------------------------
class WorkCreateView(APIView):
    template_name = "teacher_create_work.html"
    
    def get(self, request):
        user_id = request.session.get('user_id')  # ✅ Fixed: get User ID
        if not user_id:
            return redirect("teacher_login")
                    
        # ✅ Fixed: get Teacher by user__id
        try:
            teacher = Teacher.objects.get(user__id=user_id)
        except Teacher.DoesNotExist:
            messages.error(request, "Teacher profile not found")
            return redirect("teacher_login")
                    
        classes = Course.objects.all()
        return render(request, self.template_name, {"classes": classes})
    
    def post(self, request):
        user_id = request.session.get('user_id')  # ✅ Fixed: get User ID
        if not user_id:
            return redirect("teacher_login")

        # ✅ Fixed: get Teacher by user__id
        try:
            teacher = Teacher.objects.get(user__id=user_id)
        except Teacher.DoesNotExist:
            messages.error(request, "Teacher profile not found")
            return redirect("teacher_login")

        class_id = request.POST.get("class_name")
        title = request.POST.get("title")
        description = request.POST.get("description")
        file = request.FILES.get("work_file")

        if not all([class_id, title, description]):
            messages.error(request, "All fields are required")
            return self.get(request)

        course = get_object_or_404(Course, id=class_id)

        Work.objects.create(
            teacher=teacher,
            course=course,
            title=title,
            description=description,
            work_file=file,
        )
        
        # ✅ SUCCESS MESSAGE PART ADDED HERE
        messages.success(request, f'Assignment "{title}" created successfully!')
        
        return redirect("teacher_create_work")

# ----------------------------
# 2. Teacher: List Works
# ----------------------------
class WorkListTeacherView(APIView):
    template_name = "teacher_work_list.html"

    def get(self, request):
        user_id = request.session.get('user_id')  # ✅ Fixed: get User ID
        if not user_id:
            return redirect("teacher_login")

        # ✅ Fixed: get Teacher by user__id
        try:
            teacher = Teacher.objects.get(user__id=user_id)
        except Teacher.DoesNotExist:
            messages.error(request, "Teacher profile not found")
            return redirect("teacher_login")

        works = Work.objects.filter(teacher=teacher).order_by("-created_at")
        return render(request, self.template_name, {"works": works})

# ----------------------------
# 3. Teacher: Work Detail + Submissions
# ----------------------------
class WorkDetailTeacherView(APIView):
    template_name = "teacher_work_detail.html"

    def get(self, request, pk):
        user_id = request.session.get('user_id')  # ✅ Fixed: get User ID
        if not user_id:
            return redirect("teacher_login")

        # ✅ Fixed: get Teacher by user__id
        try:
            teacher = Teacher.objects.get(user__id=user_id)
        except Teacher.DoesNotExist:
            messages.error(request, "Teacher profile not found")
            return redirect("teacher_login")

        work = get_object_or_404(Work, id=pk, teacher=teacher)

        submissions = Submission.objects.filter(work=work)
        students = StudentRegistration.objects.filter(class_name=work.course)

        student_submissions = []
        for student in students:
            submission = submissions.filter(student=student).first()
            student_submissions.append({
                "student": student,
                "submission": submission
            })

        return render(request, self.template_name, {
            "work": work,
            "student_submissions": student_submissions,
        })

    def post(self, request, pk):
        user_id = request.session.get('user_id')  # ✅ Fixed: get User ID
        if not user_id:
            return redirect("teacher_login")

        # ✅ Fixed: get Teacher by user__id
        try:
            teacher = Teacher.objects.get(user__id=user_id)
        except Teacher.DoesNotExist:
            messages.error(request, "Teacher profile not found")
            return redirect("teacher_login")

        work = get_object_or_404(Work, id=pk, teacher=teacher)

        submission_id = request.POST.get("submission_id")
        action = request.POST.get("action")
        
        if not submission_id or not action:
            messages.error(request, "Invalid submission data")
            return redirect("teacher_work_detail", pk=pk)
            
        submission = get_object_or_404(Submission, id=submission_id, work=work)

        if action == "accept":
            submission.status = "ACCEPTED"
            messages.success(request, f"Accepted submission from {submission.student.full_name}")
        elif action == "reject":
            submission.status = "REJECTED" 
            messages.success(request, f"Rejected submission from {submission.student.full_name}")
        else:
            messages.error(request, "Invalid action")
            return redirect("teacher_work_detail", pk=pk)
            
        submission.save()

        # ✅ FIXED: Using correct URL name from urls.py
        return redirect("teacher_work_detail", pk=pk)

# ----------------------------
# 4. Student: Submit Work
# ----------------------------
class SubmissionCreateView(APIView):
    template_name = "student_submit_work.html"

    def get(self, request, work_id):
        work = get_object_or_404(Work, id=work_id)
        return render(request, self.template_name, {"work": work})

    def post(self, request, work_id):
        student_id = request.session.get("student_id")
        if not student_id:
            return redirect("login")

        student = get_object_or_404(StudentRegistration, id=student_id)
        work = get_object_or_404(Work, id=work_id)
        file = request.FILES.get("answer_file")

        if not file:
            messages.error(request, "File is required")
            return render(request, self.template_name, {"work": work})

        # Create or update submission
        submission, created = Submission.objects.get_or_create(
            work=work,
            student=student,
            defaults={"answer_file": file, "status": "REVIEWING"}  # ✅ Keep as REVIEWING to match template
        )

        if not created:
            submission.answer_file = file
            submission.status = "REVIEWING"  # ✅ Keep as REVIEWING to match template
            submission.save()

        messages.success(request, "Work submitted successfully!")
        return redirect("profile")

# ----------------------------
# 5. Student: List Works
# ----------------------------
class WorkListStudentView(APIView):
    template_name = "student_work_list.html"

    def get(self, request):
        student_id = request.session.get("student_id")
        if not student_id:
            return redirect("login")

        student = get_object_or_404(StudentRegistration, id=student_id)
        works = Work.objects.filter(course=student.class_name).order_by("-created_at")

        submissions = Submission.objects.filter(student=student)
        submission_map = {s.work.id: s for s in submissions}

        return render(request, self.template_name, {
            "works": works,
            "submission_map": submission_map,
        })