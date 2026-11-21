import logging
from skill_analysis.models import Analysis, Message
from skill_analysis.services.llm import call_llm

logger = logging.getLogger(__name__)


def answer_user_query(analysis: Analysis, user_message_text: str) -> str:
    """
    Module 7: AI Career Assistant grounded in the user's analysis.
    Builds context from match score, gaps, roadmap items and progress,
    and maintains the last 6 messages for continuity.
    """
    # 1. Save user message
    user_msg = Message.objects.create(
        analysis=analysis,
        role='user',
        content=user_message_text.strip()
    )

    # 2. Gather context
    gaps = list(analysis.gaps.select_related('jd_skill', 'closest_resume_skill').all())
    matched = [g.jd_skill.name for g in gaps if g.status == 'matched']
    partial = [f"{g.jd_skill.name} (closest: {g.closest_resume_skill.name if g.closest_resume_skill else 'none'})" for g in gaps if g.status == 'partial']
    missing = [g.jd_skill.name for g in gaps if g.status == 'missing']

    # Roadmap progress context
    roadmap_summary = []
    if hasattr(analysis, 'roadmap'):
        for phase in analysis.roadmap.phases.prefetch_related('items').all():
            items_str = ", ".join([f"{item.skill} [{item.status}]" for item in phase.items.all()])
            roadmap_summary.append(f"{phase.title}: {items_str}")

    context_str = (
        f"Target Job Role: {analysis.jd.title}\n"
        f"Overall Match Score: {analysis.match_score:.1f}%\n"
        f"Matched Skills: {', '.join(matched) if matched else 'None'}\n"
        f"Partial Skills to Improve: {', '.join(partial) if partial else 'None'}\n"
        f"Missing Skills to Learn: {', '.join(missing) if missing else 'None'}\n"
        f"Roadmap Progress: {'; '.join(roadmap_summary) if roadmap_summary else 'No roadmap yet'}\n"
    )

    system_prompt = (
        "You are an encouraging, experienced, and highly pragmatic AI Career Coach. "
        "Ground your advice strictly in the candidate's analysis and progress data provided below. "
        "Offer specific actionable steps, suggest learning techniques, clarify missing skills, and give practical interview preparation advice. "
        "Keep responses structured, inspiring, and concise.\n\n"
        f"=== CANDIDATE CONTEXT ===\n{context_str}\n========================="
    )

    # 3. Retrieve last 6 messages for conversation continuity
    recent_messages = list(Message.objects.filter(analysis=analysis).order_by('-created_at')[:6])
    recent_messages.reverse()

    history_prompt = ""
    for m in recent_messages:
        prefix = "Student" if m.role == 'user' else "Coach"
        history_prompt += f"{prefix}: {m.content}\n"

    history_prompt += "Coach:"

    response_text = call_llm(
        prompt=history_prompt,
        system_prompt=system_prompt,
        json_mode=False
    )

    # 4. Save assistant response
    Message.objects.create(
        analysis=analysis,
        role='assistant',
        content=response_text.strip()
    )

    return response_text.strip()
