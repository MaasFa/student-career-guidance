from django.db import models
from django.contrib.auth.models import User
from mentors.models import Mentor

class StudentQuery(models.Model):

    STATUS_CHOICES = [
        ("open", "Open"),
        ("accepted", "Accepted"),
        ("scheduled", "Scheduled"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="student_queries"
    )

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField()

    subject = models.CharField(
        max_length=100
    )

    topic = models.CharField(
        max_length=150
    )

    query = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.name} - {self.topic}"

class Session(models.Model):

    STATUS_CHOICES = [
        ("offered", "Offered"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    student_query = models.OneToOneField(
        StudentQuery,
        on_delete=models.CASCADE,
        related_name="session"
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="personal_sessions"
    )

    mentor = models.ForeignKey(
        Mentor,
        on_delete=models.CASCADE,
        related_name="personal_sessions"
    )

    date = models.DateField(
        null=True,
        blank=True
    )

    start_time = models.TimeField(
        null=True,
        blank=True
    )

    end_time = models.TimeField(
        null=True,
        blank=True
    )

    meeting_link = models.URLField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="offered"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.student.username} - {self.mentor.name}"