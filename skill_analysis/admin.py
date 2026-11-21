from django.contrib import admin
from .models import (
    Resume, JobDescription, Analysis, Skill, AnalysisSkill,
    SkillGap, Roadmap, Phase, RoadmapItem, Message
)


class AnalysisSkillInline(admin.TabularInline):
    model = AnalysisSkill
    extra = 0


class SkillGapInline(admin.TabularInline):
    model = SkillGap
    extra = 0


class RoadmapItemInline(admin.TabularInline):
    model = RoadmapItem
    extra = 0


class PhaseInline(admin.StackedInline):
    model = Phase
    extra = 0


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_jd_title', 'match_score', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('jd__title', 'user__username')
    inlines = [AnalysisSkillInline, SkillGapInline]

    def get_jd_title(self, obj):
        return obj.jd.title
    get_jd_title.short_description = 'Target Job'


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'file_type', 'created_at')
    search_fields = ('user__username', 'file')


@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'created_at')
    search_fields = ('title', 'user__username')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    search_fields = ('name', 'category')
    list_filter = ('category',)


@admin.register(SkillGap)
class SkillGapAdmin(admin.ModelAdmin):
    list_display = ('analysis', 'jd_skill', 'closest_resume_skill', 'similarity', 'status')
    list_filter = ('status',)


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ('id', 'analysis', 'title', 'created_at')
    inlines = [PhaseInline]


@admin.register(RoadmapItem)
class RoadmapItemAdmin(admin.ModelAdmin):
    list_display = ('skill', 'phase', 'est_hours', 'status')
    list_filter = ('status', 'phase')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('analysis', 'role', 'created_at')
    list_filter = ('role', 'created_at')
