from django.db import models
from django.contrib.auth.models import User


class Mentor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="mentor_profile"
    )

    name = models.CharField(max_length=100)

    expertise = models.CharField(max_length=255)

    bio = models.TextField()

    experience = models.PositiveIntegerField(
        help_text="Experience in years"
    )

    profile_image = models.ImageField(
        upload_to="mentors/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name
class Availability(models.Model):
    mentor = models.ForeignKey(
        Mentor,
        on_delete=models.CASCADE,
        related_name="availabilities"
    )

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.mentor.name} - {self.date} {self.start_time}"

class SessionBooking(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="session_bookings"
    )

    mentor = models.ForeignKey(
        Mentor,
        on_delete=models.CASCADE,
        related_name="session_bookings"
    )

    availability = models.ForeignKey(
        Availability,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    topic = models.CharField(max_length=255)

    meeting_link = models.URLField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.student.username} - {self.mentor.name} - {self.availability.date}"    