from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.utils.timezone import localdate
from datetime import datetime
from cources.models import Course   # ✅ Correct import
from myapp.models import StudentRegistration
from .models import Attendance


class AttendanceMarkView(View):
    template_name = "attendance_mark.html"

    def get(self, request):
        courses = Course.objects.all()   # ✅ FIX here
        students = []
        class_id = request.GET.get("class_id")
        date = request.GET.get("date", localdate())  # default to today

        if class_id:
            students = StudentRegistration.objects.filter(class_name_id=class_id)

        return render(request, self.template_name, {
            "courses": courses,
            "students": students,
            "today": localdate(),
            "selected_class": class_id,
            "selected_date": date,
        })

    def post(self, request):
        class_id = request.POST.get("class_id")
        date = request.POST.get("date", localdate())
        students = StudentRegistration.objects.filter(class_name_id=class_id)

        for student in students:
            status = request.POST.get(f"attendance_{student.id}", "absent")
            Attendance.objects.update_or_create(
                student=student,
                date=date,
                defaults={"status": status}
            )

        messages.success(request, "Attendance marked successfully!")
        return redirect("attendance-list")


class AttendanceListView(View):
    template_name = "attendance_list.html"

    def get(self, request):
        courses = Course.objects.all()   # ✅ FIX here
        class_id = request.GET.get("class_id")
        date_str = request.GET.get("date")

        if date_str:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                date = localdate()
        else:
            date = localdate()

        attendance_records = []
        if class_id:
            students = StudentRegistration.objects.filter(class_name_id=class_id)
            attendance_records = Attendance.objects.filter(
                student__in=students,
                date=date
            ).select_related("student", "student__class_name")

        return render(request, self.template_name, {
            "courses": courses,
            "attendance_records": attendance_records,
            "selected_class": class_id,
            "selected_date": date,
            "today": localdate(),
        })
