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
        print("=" * 50)
        print("ATTENDANCE POST REQUEST STARTED")
        print("=" * 50)
        
        class_id = request.POST.get("class_id")
        date_str = request.POST.get("date")
        
        # Debug prints
        print(f"Raw POST Data: {dict(request.POST)}")
        print(f"Class ID: {class_id}")
        print(f"Date string: {date_str}")
        
        # Validate required fields
        if not class_id:
            messages.error(request, "Please select a class.")
            print("ERROR: No class_id provided")
            return redirect("attendance-mark")
            
        # Handle date conversion
        if date_str:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                print(f"Parsed date: {date} (type: {type(date)})")
            except ValueError as e:
                print(f"Date parsing error: {e}")
                date = localdate()
                messages.warning(request, "Invalid date format. Using today's date.")
        else:
            date = localdate()
            print(f"Using default date: {date}")

        # Get students
        try:
            students = StudentRegistration.objects.filter(class_name_id=class_id)
            print(f"Found {students.count()} students for class_id {class_id}")
            
            if not students.exists():
                print("WARNING: No students found!")
                messages.warning(request, "No students found for this class.")
                return redirect("attendance-mark")
            
            # Print student details
            for student in students:
                print(f"  - Student: {student.name} (ID: {student.id})")
                
        except Exception as e:
            print(f"ERROR getting students: {e}")
            messages.error(request, "Error retrieving students.")
            return redirect("attendance-mark")

        # Process attendance for each student
        attendance_saved_count = 0
        attendance_errors = []
        
        try:
            with transaction.atomic():  # Use transaction for data integrity
                for student in students:
                    attendance_key = f"attendance_{student.id}"
                    status = request.POST.get(attendance_key, "absent")
                    
                    print(f"\nProcessing student: {student.name}")
                    print(f"  - Looking for key: {attendance_key}")
                    print(f"  - Status received: {status}")
                    
                    try:
                        # Check if attendance already exists
                        existing_attendance = Attendance.objects.filter(
                            student=student,
                            date=date
                        ).first()
                        
                        if existing_attendance:
                            print(f"  - Found existing record: {existing_attendance.status} -> {status}")
                        else:
                            print(f"  - Creating new record with status: {status}")
                        
                        # Save or update attendance
                        attendance_obj, created = Attendance.objects.update_or_create(
                            student=student,
                            date=date,
                            defaults={"status": status}
                        )
                        
                        if created:
                            print(f"  ✅ CREATED new attendance record for {student.name}")
                        else:
                            print(f"  ✅ UPDATED attendance record for {student.name}")
                            
                        # Verify the save
                        saved_record = Attendance.objects.get(
                            student=student,
                            date=date
                        )
                        print(f"  - Verified saved record: {saved_record.status}")
                        
                        attendance_saved_count += 1
                        
                    except Exception as e:
                        error_msg = f"Error saving attendance for {student.name}: {e}"
                        print(f"  ❌ {error_msg}")
                        attendance_errors.append(error_msg)
                        
        except Exception as e:
            print(f"TRANSACTION ERROR: {e}")
            messages.error(request, f"Database error: {e}")
            return redirect("attendance-mark")

        print(f"\nSUMMARY:")
        print(f"Total attendance records processed: {attendance_saved_count}")
        print(f"Errors encountered: {len(attendance_errors)}")
        
        if attendance_errors:
            for error in attendance_errors:
                print(f"  - {error}")
            messages.warning(request, f"Attendance marked for {attendance_saved_count} students, but {len(attendance_errors)} errors occurred.")
        else:
            messages.success(request, f"Attendance marked successfully for {attendance_saved_count} students!")
        
        # Final verification - count records in database
        final_count = Attendance.objects.filter(date=date).count()
        print(f"Total attendance records in DB for {date}: {final_count}")
        
        print("=" * 50)
        print("ATTENDANCE POST REQUEST COMPLETED")
        print("=" * 50)
        
        # Redirect with parameters to see the saved data
        url = reverse('attendance-list') + f'?class_id={class_id}&date={date}'
        return HttpResponseRedirect(url)


class AttendanceListView(View):
    template_name = "attendance_list.html"

    def get(self, request):
        print(f"\nATTENDANCE LIST VIEW - GET request")
        print(f"GET parameters: {dict(request.GET)}")
        
        courses = Course.objects.all()
        class_id = request.GET.get("class_id")
        date_str = request.GET.get("date")

        if date_str:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                print(f"Parsed date for list view: {date}")
            except ValueError:
                date = localdate()
                print(f"Date parsing failed, using today: {date}")
        else:
            date = localdate()
            print(f"No date provided, using today: {date}")

        attendance_records = []
        if class_id:
            students = StudentRegistration.objects.filter(class_name_id=class_id)
            attendance_records = Attendance.objects.filter(
                student__in=students,
                date=date
            ).select_related("student", "student__class_name")
            
            print(f"Found {attendance_records.count()} attendance records for class {class_id} on {date}")
            for record in attendance_records:
                print(f"  - {record.student.name}: {record.status}")
        
        # Also check total records in database
        total_records = Attendance.objects.all().count()
        print(f"Total attendance records in entire database: {total_records}")

        return render(request, self.template_name, {
            "courses": courses,
            "attendance_records": attendance_records,
            "selected_class": class_id,
            "selected_date": date,
            "today": localdate(),
        })