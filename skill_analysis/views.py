import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required

from .models import (
    Resume, JobDescription, Analysis, Skill, AnalysisSkill,
    SkillGap, Roadmap, Phase, RoadmapItem, Message
)
from .forms import AnalysisUploadForm
from .services.ingestion import extract_resume_text, clean_job_description
from .services.extractor import process_and_store_skills
from .services.gap_analyzer import run_gap_analysis
from .services.roadmap_generator import generate_roadmap_for_analysis
from .services.assistant import answer_user_query

logger = logging.getLogger(__name__)


def get_user_or_none(request):
    return request.user if request.user.is_authenticated else None


def dashboard_view(request):
    """
    Overview dashboard:
    - New Analysis Upload form
    - Past analysis history list
    - Summary metrics
    """
    user = get_user_or_none(request)
    form = AnalysisUploadForm()

    if user:
        analyses = Analysis.objects.filter(user=user).select_related('jd').order_by('-created_at')
    else:
        # Show session-based or recent analyses
        analyses = Analysis.objects.select_related('jd').order_by('-created_at')[:10]

    total_analyses = analyses.count()
    highest_match = max([a.match_score for a in analyses], default=0.0)

    context = {
        "form": form,
        "analyses": analyses,
        "total_analyses": total_analyses,
        "highest_match": round(highest_match, 1),
    }
    return render(request, "skill_analysis/dashboard.html", context)


@require_POST
def create_analysis_view(request):
    """
    Processes resume + JD upload through the ingestion, extraction,
    gap detection, and roadmap generation pipeline.
    """
    form = AnalysisUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        for field, errors in form.errors.items():
            for err in errors:
                messages.error(request, f"{field.replace('_', ' ').capitalize()}: {err}")
        return redirect("skill_analysis:dashboard")

    title = form.cleaned_data["title"]
    resume_file = form.cleaned_data["resume_file"]
    jd_raw_text = form.cleaned_data["jd_text"]
    user = get_user_or_none(request)

    # 1. Ingestion
    try:
        extracted_resume_text, file_type = extract_resume_text(resume_file)
        cleaned_jd = clean_job_description(jd_raw_text)
    except ValueError as ve:
        messages.error(request, str(ve))
        return redirect("skill_analysis:dashboard")
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        messages.error(request, f"An unexpected error occurred during document parsing: {str(e)}")
        return redirect("skill_analysis:dashboard")

    # 2. Database model creation
    resume_obj = Resume.objects.create(
        user=user,
        file=resume_file,
        extracted_text=extracted_resume_text,
        file_type=file_type
    )

    jd_obj = JobDescription.objects.create(
        user=user,
        title=title,
        text=cleaned_jd
    )

    analysis_obj = Analysis.objects.create(
        user=user,
        resume=resume_obj,
        jd=jd_obj,
        status="processing"
    )

    # 3. Pipeline execution
    try:
        # Module 2: Skill Extraction
        process_and_store_skills(analysis_obj)

        # Module 3: Semantic Gap Detection
        gap_results = run_gap_analysis(analysis_obj)

        # Module 4: Roadmap Generation
        generate_roadmap_for_analysis(analysis_obj)

        analysis_obj.status = "completed"
        analysis_obj.save(update_fields=['status'])
        messages.success(request, f"Analysis for '{title}' completed successfully!")
        return redirect("skill_analysis:analysis_detail", analysis_id=analysis_obj.id)

    except Exception as e:
        logger.exception(f"Pipeline error for analysis #{analysis_obj.id}: {e}")
        analysis_obj.status = "failed"
        analysis_obj.error_message = str(e)
        analysis_obj.save(update_fields=['status', 'error_message'])
        messages.error(request, f"Failed to complete skill analysis: {str(e)}")
        return redirect("skill_analysis:dashboard")


def analysis_detail_view(request, analysis_id):
    """
    Module 6: Comprehensive single-page dashboard and visualization
    """
    analysis = get_object_or_404(
        Analysis.objects.select_related('resume', 'jd').prefetch_related('gaps__jd_skill', 'gaps__closest_resume_skill'),
        id=analysis_id
    )

    gaps = list(analysis.gaps.all())
    matched_gaps = [g for g in gaps if g.status == 'matched']
    partial_gaps = [g for g in gaps if g.status == 'partial']
    missing_gaps = [g for g in gaps if g.status == 'missing']

    # Module 4 & 5: Roadmap & phases
    roadmap = getattr(analysis, 'roadmap', None)
    phases = []
    if roadmap:
        phases = roadmap.phases.prefetch_related('items').order_by('order')

    # Module 7: AI Assistant chat messages
    chat_messages = analysis.messages.order_by('created_at')

    # Breakdown chart counts
    counts = {
        "matched": len(matched_gaps),
        "partial": len(partial_gaps),
        "missing": len(missing_gaps),
        "total": len(gaps),
    }

    context = {
        "analysis": analysis,
        "gaps": gaps,
        "matched_gaps": matched_gaps,
        "partial_gaps": partial_gaps,
        "missing_gaps": missing_gaps,
        "roadmap": roadmap,
        "phases": phases,
        "chat_messages": chat_messages,
        "counts": counts,
    }
    return render(request, "skill_analysis/analysis_detail.html", context)


@require_POST
def update_roadmap_item_status(request, item_id):
    """
    Module 5: HTMX endpoint for live status updates on roadmap items
    Calculates phase progress and hours-weighted overall progress.
    """
    item = get_object_or_404(RoadmapItem.objects.select_related('phase__roadmap'), id=item_id)
    new_status = request.POST.get("status")

    if new_status in ['todo', 'in_progress', 'done']:
        item.status = new_status
        item.save(update_fields=['status'])

    phase = item.phase
    roadmap = phase.roadmap

    phase_progress = phase.progress_percentage()
    overall_progress = roadmap.overall_progress_percentage()

    # If HTMX request, return the refreshed item + progress components
    if request.headers.get("HX-Request"):
        return render(request, "skill_analysis/partials/roadmap_item_row.html", {
            "item": item,
            "phase": phase,
            "roadmap": roadmap,
            "phase_progress": phase_progress,
            "overall_progress": overall_progress,
        })

    return JsonResponse({
        "success": True,
        "item_id": item.id,
        "status": item.status,
        "phase_progress": phase_progress,
        "overall_progress": overall_progress
    })


@require_POST
def chat_assistant_view(request, analysis_id):
    """
    Module 7: Interactive AI Career Assistant chat endpoint
    """
    analysis = get_object_or_404(Analysis, id=analysis_id)
    user_query = request.POST.get("message", "").strip()

    if not user_query:
        if request.headers.get("HX-Request"):
            return HttpResponse("")
        return JsonResponse({"error": "Empty message"}, status=400)

    try:
        assistant_reply = answer_user_query(analysis, user_query)
    except Exception as e:
        logger.error(f"AI Assistant error: {e}")
        assistant_reply = "I'm having a little trouble connecting right now, but please review your roadmap and missing skill gaps to focus on your core priorities!"

    if request.headers.get("HX-Request"):
        recent_two = list(Message.objects.filter(analysis=analysis).order_by('-created_at')[:2])
        recent_two.reverse()
        return render(request, "skill_analysis/partials/chat_messages_pair.html", {
            "messages": recent_two
        })

    return JsonResponse({
        "reply": assistant_reply
    })


@require_POST
def delete_analysis_view(request, analysis_id):
    """Deletes an analysis and redirects to dashboard."""
    analysis = get_object_or_404(Analysis, id=analysis_id)
    title = analysis.jd.title
    analysis.delete()
    messages.success(request, f"Analysis for '{title}' was deleted.")
    return redirect("skill_analysis:dashboard")
