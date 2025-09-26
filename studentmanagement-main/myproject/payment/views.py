# payment/views.py

import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import ExamPayment
from Exam.models import Exam
from myapp.models import StudentRegistration

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch


# Razorpay client init (use keys from settings.py)
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)
class PaymentSelectView(View):
    template_name = "payment/payment_select.html"

    def get(self, request):
        exams = Exam.objects.all()
        return render(request, self.template_name, {"exams": exams})

    def post(self, request):
        exam_id = request.POST.get("exam_id")
        method = request.POST.get("method")
        amount_input = request.POST.get("amount")  # user-entered amount
        student_id = request.session.get("user_id")

        if not exam_id or not method:
            messages.error(request, "Please select exam and payment method.")
            return redirect("payment-select")

        exam = get_object_or_404(Exam, id=exam_id)
        student = get_object_or_404(StudentRegistration, id=student_id)

        # Prevent duplicate payment
        if ExamPayment.objects.filter(student=student, exam=exam).exists():
            messages.warning(request, "Payment already initiated for this exam.")
            return redirect("payment-select")

        # Determine amount: user input takes priority, fallback to exam default
        if amount_input:
            try:
                amount = float(amount_input)
            except ValueError:
                messages.error(request, "Invalid amount entered.")
                return redirect("payment-select")
        else:
            amount = getattr(exam, "amount", 500)  # default ₹500 if not defined

        if method == "cash":
            ExamPayment.objects.create(
                student=student,
                exam=exam,
                method="cash",
                status="pending",
                amount=amount,  # store actual rupee amount
            )
            messages.success(
                request, f"Cash payment request  sent. Awaiting admin approval."
            )
            return redirect("payment-select")

        elif method == "razorpay":
            # Create Razorpay order (amount in paise)
            order = razorpay_client.order.create(
                {
                    "amount": int(amount * 100),
                    "currency": "INR",
                    "payment_capture": "1",
                }
            )

            payment = ExamPayment.objects.create(
                student=student,
                exam=exam,
                method="razorpay",
                status="pending",
                amount=amount,
                razorpay_order_id=order["id"],
            )

            return render(
                request,
                "payment_razorpay.html",
                {
                    "exam": exam,
                    "payment": payment,
                    "razorpay_key": settings.RAZORPAY_KEY_ID,
                    "order": order,
                },
            )

        else:
            messages.error(request, "Invalid payment method.")
            return redirect("payment-select")

@method_decorator(csrf_exempt, name="dispatch")
class RazorpayCallbackView(View):
    def post(self, request):
        data = request.POST
        try:
            payment = ExamPayment.objects.get(razorpay_order_id=data.get("razorpay_order_id"))
        except ExamPayment.DoesNotExist:
            return HttpResponseBadRequest("Payment record not found")

        params_dict = {
            "razorpay_order_id": data.get("razorpay_order_id"),
            "razorpay_payment_id": data.get("razorpay_payment_id"),
            "razorpay_signature": data.get("razorpay_signature"),
        }

        try:
            # Verify signature
            razorpay_client.utility.verify_payment_signature(params_dict)
            payment.status = "success"
            payment.razorpay_payment_id = data.get("razorpay_payment_id")
            payment.razorpay_signature = data.get("razorpay_signature")
            payment.save()
            messages.success(request, "Payment successful!")
        except:
            payment.status = "failed"
            payment.save()
            messages.error(request, "Payment failed!")

        return redirect("payment-select")

class AdminCashApprovalView(View):
    template_name = "admin_payments.html"

    def get(self, request):
        pending_cash = ExamPayment.objects.filter(method="cash", status="pending")
        return render(request, self.template_name, {"payments": pending_cash})  # fixed key name

    def post(self, request, pk):
        payment = get_object_or_404(ExamPayment, id=pk, method="cash", status="pending")
        action = request.POST.get("action")

        if action == "approve":
            payment.status = "approved"
            messages.success(request, f"Payment approved for {payment.student.username}.")
        else:
            payment.status = "failed"
            messages.warning(request, f"Payment rejected for {payment.student.username}.")

        payment.save()
        return redirect("payment-admin")

#alterned





class HallTicketView(View):
    def get(self, request, exam_id):
        student_id = request.session.get("user_id")
        if not student_id:
            messages.error(request, "You must be logged in.")
            return redirect("payment-select")

        student = get_object_or_404(StudentRegistration, id=student_id)
        exam = get_object_or_404(Exam, id=exam_id)

        # Check payment
        try:
            payment = ExamPayment.objects.get(student=student, exam=exam)
        except ExamPayment.DoesNotExist:
            messages.error(request, "No payment record found.")
            return redirect("payment-select")

        if payment.status not in ["success", "approved"]:
            messages.error(request, "Payment not completed. Hall ticket unavailable.")
            return redirect("payment-select")

        # Create PDF response
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="hall_ticket_{student.username}_{exam.id}.pdf"'
        )

        # Build PDF
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 80, "Examination Hall Ticket")

        # Student details (✅ fixed fields)
        p.setFont("Helvetica", 12)
        p.drawString(100, height - 150, f"Name: {student.name}")
        p.drawString(100, height - 180, f"Class: {student.class_name}")
        p.drawString(100, height - 210, f"Exam: {exam.title}")
        p.drawString(100, height - 240, f"Date: {exam.date.strftime('%d-%m-%Y')}")

        # Footer
        p.setFont("Helvetica-Oblique", 10)
        

        p.showPage()
        p.save()
        return response
