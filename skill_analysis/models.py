from django.db import models
from django.contrib.auth.models import User


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resumes", null=True, blank=True)
    file = models.FileField(upload_to="resumes/")
    extracted_text = models.TextField()
    file_type = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        filename = self.file.name.split('/')[-1] if self.file else "Unnamed"
        return f"Resume ({filename}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class JobDescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="job_descriptions", null=True, blank=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d')})"


class Analysis(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="analyses", null=True, blank=True)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="analyses")
    jd = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name="analyses")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    match_score = models.FloatField(default=0.0)
    summary = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Analysis #{self.id} - {self.jd.title} ({self.match_score:.1f}%)"


class Skill(models.Model):
    name = models.CharField(max_length=150, unique=True)
    category = models.CharField(max_length=100, blank=True, default='General')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category})"


class AnalysisSkill(models.Model):
    SOURCE_CHOICES = [
        ('resume', 'Resume'),
        ('jd', 'Job Description'),
    ]
    IMPORTANCE_CHOICES = [
        ('required', 'Required'),
        ('nice_to_have', 'Nice To Have'),
        ('standard', 'Standard'),
    ]

    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name="analysis_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="occurrences")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    importance = models.CharField(max_length=20, choices=IMPORTANCE_CHOICES, default='standard')
    level = models.CharField(max_length=50, blank=True, default='intermediate')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['analysis', 'skill', 'source'], name='unique_analysis_skill_source')
        ]

    def __str__(self):
        return f"{self.skill.name} [{self.source}] ({self.importance})"


class SkillGap(models.Model):
    STATUS_CHOICES = [
        ('matched', 'Matched'),
        ('partial', 'Partial'),
        ('missing', 'Missing'),
    ]

    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name="gaps")
    jd_skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="jd_gaps")
    closest_resume_skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True, blank=True, related_name="matched_gaps")
    similarity = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-similarity']

    def __str__(self):
        return f"{self.jd_skill.name} -> {self.status} ({self.similarity:.2f})"


class Roadmap(models.Model):
    analysis = models.OneToOneField(Analysis, on_delete=models.CASCADE, related_name="roadmap")
    title = models.CharField(max_length=255, default="Personalized Career Learning Roadmap")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Roadmap for Analysis #{self.analysis_id}"

    def total_hours(self):
        return sum(item.est_hours for phase in self.phases.all() for item in phase.items.all())

    def done_hours(self):
        return sum(item.est_hours for phase in self.phases.all() for item in phase.items.filter(status='done'))

    def overall_progress_percentage(self):
        total = self.total_hours()
        if total == 0:
            return 0
        return round((self.done_hours() / total) * 100)


class Phase(models.Model):
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name="phases")
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Phase {self.order}: {self.title}"

    def progress_percentage(self):
        total = self.items.count()
        if total == 0:
            return 0
        done = self.items.filter(status='done').count()
        return round((done / total) * 100)


class RoadmapItem(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name="items")
    skill = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resources = models.TextField(blank=True)
    est_hours = models.PositiveIntegerField(default=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.skill} ({self.status})"


class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role.capitalize()}: {self.content[:30]}..."
