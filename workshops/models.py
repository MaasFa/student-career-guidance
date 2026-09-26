from django.db import models
from django.contrib.auth.models import User
from mentors.models import Mentor


class Workshop(models.Model):

    SESSION_TYPES = [
        ("lecture", "Lecture"),
        ("workshop", "Workshop"),
    ]

    STATUS_CHOICES = [
        ("published", "Published"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    mentor = models.ForeignKey(
        Mentor,
        on_delete=models.CASCADE,
        related_name="workshops"
    )

    title = models.CharField(max_length=200)

    topic = models.CharField(max_length=100)

    description = models.TextField()

    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPES,
        default="lecture"
    )

    date = models.DateField()

    start_time = models.TimeField()

    duration = models.PositiveIntegerField(
        help_text="Duration in minutes"
    )

    meeting_link = models.URLField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="published"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title