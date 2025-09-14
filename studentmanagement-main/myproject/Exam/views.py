from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Exam , ExamResponse
from .serializers import ExamSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib import messages

class ExamListView(APIView):
    template_name = "exam_list.html"

    def get(self, request):
        
        exams = Exam.objects.all()

        # exam list 
        exam_list = []
        for exam in exams:
            accepted_responses = ExamResponse.objects.filter(exam=exam, accepted=True).select_related('student')
            rejected_responses = ExamResponse.objects.filter(exam=exam, accepted=False).select_related('student')

            exam_list.append({
                "exam": exam,
                "accepted_students": [r.student for r in accepted_responses],
                "rejected_students": [r.student for r in rejected_responses],
            })

        return render(request, self.template_name, {"exam_list": exam_list})


class ExamAddView(APIView):
    template_name = "exam_add.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        title = request.POST.get("title")
        description = request.POST.get("description")
        date = request.POST.get("date")
        duration = request.POST.get("duration")

        Exam.objects.create(
            title=title,
            description=description,
            date=date,
            duration=duration
        )
        messages.success(request, "Exam added successfully!")
        return redirect("exam-list")   



class ExamEdit(APIView):
    template_name = "exam_edit.html"

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        return render(request, self.template_name, {"exam": exam})

    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        exam.title = request.POST.get("title")
        exam.description = request.POST.get("description")
        exam.date = request.POST.get("date")
        exam.duration = request.POST.get("duration")
        exam.save()
        messages.success(request, "Exam updated successfully!")
        return redirect("exam-list")



class ExamDelete(APIView):
    template_name = "exam_delete.html"

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        return render(request, self.template_name, {"exam": exam})

    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        exam.delete()
        messages.success(request, "Exam deleted successfully!")
        return redirect("exam-list")



class ExamView(APIView):
    def get(self, request):
        exams = Exam.objects.all()
        serializer = ExamSerializer(exams, many=True)
        return Response(serializer.data)
