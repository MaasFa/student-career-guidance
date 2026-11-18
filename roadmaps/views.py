from django.shortcuts import render, get_object_or_404
from .models import CareerRoadmap


def roadmap_list(request):
    roadmaps = CareerRoadmap.objects.filter(is_published=True)

    return render(
        request,
        'roadmaps/roadmap_list.html',
        {'roadmaps': roadmaps}
    )


def roadmap_detail(request, slug):
    roadmap = get_object_or_404(
        CareerRoadmap,
        slug=slug,
        is_published=True
    )

    return render(
        request,
        'roadmaps/roadmap_detail.html',
        {'roadmap': roadmap}
    )