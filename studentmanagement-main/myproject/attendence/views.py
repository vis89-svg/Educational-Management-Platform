from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.utils.timezone import localdate
from datetime import datetime
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from cources.models import Course
from myapp.models import StudentRegistration
from .models import Attendance


class AttendanceMarkView(View):
    template_name = "attendance_mark.html"

    def get(self, request):
        courses = Course.objects.all()
        students = []
        class_id = request.GET.get("class_id")
        date = request.GET.get("date", localdate())

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
        date_str = request.POST.get("date")
        
        if not class_id:
            messages.error(request, "Please select a class.")
            return redirect("attendance-mark")
            
        if date_str:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                date = localdate()
                messages.warning(request, "Invalid date format. Using today's date.")
        else:
            date = localdate()

        try:
            students = StudentRegistration.objects.filter(class_name_id=class_id)
            
            if not students.exists():
                messages.warning(request, "No students found for this class.")
                return redirect("attendance-mark")
                
        except Exception as e:
            messages.error(request, "Error retrieving students.")
            return redirect("attendance-mark")

        attendance_saved_count = 0
        attendance_errors = []
        
        try:
            with transaction.atomic():
                for student in students:
                    attendance_key = f"attendance_{student.id}"
                    status = request.POST.get(attendance_key, "absent")
                    
                    try:
                        attendance_obj, created = Attendance.objects.update_or_create(
                            student=student,
                            date=date,
                            defaults={"status": status}
                        )
                        attendance_saved_count += 1
                        
                    except Exception as e:
                        attendance_errors.append(f"Error saving attendance for {student.name}: {e}")
                        
        except Exception as e:
            messages.error(request, f"Database error: {e}")
            return redirect("attendance-mark")
        
        if attendance_errors:
            messages.warning(request, f"Attendance marked for {attendance_saved_count} students, but {len(attendance_errors)} errors occurred.")
        else:
            messages.success(request, f"Attendance marked successfully for {attendance_saved_count} students!")
        
        return redirect('attendance-list')


class AttendanceListView(View):
    template_name = "attendance_list.html"

    def get(self, request):
        courses = Course.objects.all()
        class_id = request.GET.get("class_id")
        date_str = request.GET.get("date")
        
        attendance_records = []
        selected_date = None
        show_results = False
        
        if class_id and date_str:
            try:
                selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                show_results = True
            except ValueError:
                messages.error(request, "Invalid date format.")
                show_results = False
        else:
            selected_date = None
            show_results = False

        selected_course_name = None
        if show_results and class_id:
            try:
                selected_course = courses.filter(id=class_id).first()
                if selected_course:
                    selected_course_name = selected_course.class_name
                
                students = StudentRegistration.objects.filter(class_name_id=class_id)
                attendance_records = Attendance.objects.filter(
                    student__in=students,
                    date=selected_date
                ).select_related("student", "student__class_name")
                
            except Exception as e:
                messages.error(request, "Error retrieving attendance records.")
        
        return render(request, self.template_name, {
            "courses": courses,
            "attendance_records": attendance_records,
            "selected_class": class_id,
            "selected_course_name": selected_course_name,
            "selected_date": selected_date,
            "show_results": show_results,
            "today": localdate(),
        })