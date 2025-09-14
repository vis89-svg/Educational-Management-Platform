from django.db import models
from django.utils import timezone

# Adjust the import path to where your StudentRegistration model lives
from myapp.models import StudentRegistration


class Attendance(models.Model):
    STATUS_PRESENT = "present"
    STATUS_ABSENT = "absent"

    STATUS_CHOICES = (
        (STATUS_PRESENT, "Present"),
        (STATUS_ABSENT, "Absent"),
    )

    student = models.ForeignKey(
        StudentRegistration,
        on_delete=models.CASCADE,
        related_name="attendances"
    )
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ABSENT)
    note = models.CharField(max_length=255, blank=True, null=True)  # optional remark

    class Meta:
        unique_together = ("student", "date")
        ordering = ("-date",)

    def __str__(self):
        return f"{self.student} — {self.date} — {self.status}"
