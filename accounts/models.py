# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):

    ROLE_CHOICES = [
        ("student", "Student"),
        ("mentor", "Mentor"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="student"
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    education = models.CharField(
        max_length=200,
        blank=True
    )

    career_interest = models.CharField(
        max_length=255,
        blank=True
    )

    skills = models.TextField(
        blank=True,
        help_text="Enter your skills separated by commas."
    )

    bio = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"