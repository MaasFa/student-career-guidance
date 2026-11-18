
from django.db import models
from django.utils.text import slugify


class CareerRoadmap(models.Model):

    CATEGORY_CHOICES = [
        ('IT', 'IT & Software'),
        ('DATA', 'Data Science & AI'),
        ('CORE', 'Core Engineering'),
        ('DESIGN', 'Design'),
        ('OTHER', 'Other'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    short_description = models.CharField(max_length=300)
    overview = models.TextField()

    suitable_for = models.CharField(
        max_length=300,
        help_text="Example: CSE, IT, ECE"
    )

    estimated_duration = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=50, default="Beginner")

    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class RoadmapStage(models.Model):

    roadmap = models.ForeignKey(
        CareerRoadmap,
        on_delete=models.CASCADE,
        related_name='stages'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    skills = models.TextField(
        blank=True,
        help_text="Skills covered in this stage"
    )

    duration = models.CharField(max_length=100, blank=True)
    resources = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.roadmap.title} - {self.title}"

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['roadmap', 'order'],
                name='unique_roadmap_stage_order'
            )
        ]
