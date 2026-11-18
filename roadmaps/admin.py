from django.contrib import admin
from .models import CareerRoadmap, RoadmapStage


class RoadmapStageInline(admin.TabularInline):
    model = RoadmapStage
    extra = 1


@admin.register(CareerRoadmap)
class CareerRoadmapAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'suitable_for',
        'is_published',
    )

    list_filter = ('category', 'is_published')
    search_fields = ('title', 'suitable_for')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [RoadmapStageInline]


@admin.register(RoadmapStage)
class RoadmapStageAdmin(admin.ModelAdmin):
    list_display = ('title', 'roadmap', 'order')
    list_filter = ('roadmap',)