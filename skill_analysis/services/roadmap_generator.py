import logging
from typing import Dict, Any, List
from skill_analysis.models import Analysis, SkillGap, Roadmap, Phase, RoadmapItem
from skill_analysis.services.llm import call_llm

logger = logging.getLogger(__name__)


def generate_roadmap_for_analysis(analysis: Analysis) -> Roadmap:
    """
    Generates a personalized multi-phase learning roadmap for the missing and partial skill gaps,
    using matched skills as existing contextual background.
    """
    gaps = SkillGap.objects.filter(analysis=analysis).select_related('jd_skill', 'closest_resume_skill')

    missing_skills = [g.jd_skill.name for g in gaps if g.status == 'missing']
    partial_skills = [f"{g.jd_skill.name} (partial from {g.closest_resume_skill.name if g.closest_resume_skill else 'basics'})" for g in gaps if g.status == 'partial']
    matched_skills = [g.jd_skill.name for g in gaps if g.status == 'matched']

    system_prompt = (
        "You are an expert technical curriculum designer and senior software engineering mentor. "
        "Your task is to turn technical skill gaps into an actionable, progressive learning roadmap. "
        "Structure the learning plan into 3 sequential phases: "
        "1. Foundations (prerequisites, underlying theory, essential syntax) "
        "2. Core (primary missing frameworks, deep dive into essential requirements) "
        "3. Advanced (complex system design, portfolio project, interview readiness). "
        "Ensure all missing and partial skills are systematically addressed. "
        "Return STRICT valid JSON only matching this schema:\n"
        "{\n"
        '  "title": "Roadmap Title",\n'
        '  "phases": [\n'
        '    {\n'
        '      "title": "Phase 1: Foundations",\n'
        '      "order": 1,\n'
        '      "items": [\n'
        '        {\n'
        '          "skill": "Skill Name",\n'
        '          "description": "Short explanation of what to learn",\n'
        '          "resources": "Recommended course, tutorial, or documentation link",\n'
        '          "est_hours": 12\n'
        '        }\n'
        '      ]\n'
        '    }\n'
        '  ]\n'
        "}"
    )

    prompt = (
        f"Target Job Role: {analysis.jd.title}\n\n"
        f"Existing Matched Skills (User already knows): {', '.join(matched_skills) if matched_skills else 'None'}\n"
        f"Partial Skill Gaps to Upgrade: {', '.join(partial_skills) if partial_skills else 'None'}\n"
        f"Missing Skill Gaps to Learn from Scratch: {', '.join(missing_skills) if missing_skills else 'None'}\n\n"
        "Generate a structured 3-phase roadmap ordered by prerequisites and importance. "
        "Provide realistic estimated hours for each item and reputable learning resources. Output JSON only."
    )

    result = call_llm(prompt, system_prompt=system_prompt, json_mode=True, max_retries=1)

    # Clean previous roadmap if regenerating
    if hasattr(analysis, 'roadmap'):
        analysis.roadmap.delete()

    title = "Personalized Learning Roadmap"
    phases_data = []

    if isinstance(result, dict):
        title = result.get("title", f"Roadmap for {analysis.jd.title}")
        phases_data = result.get("phases", [])

    roadmap = Roadmap.objects.create(
        analysis=analysis,
        title=title
    )

    if not phases_data:
        # Fallback default phases if LLM yielded empty
        phases_data = [
            {
                "title": "Phase 1: Foundations",
                "order": 1,
                "items": [
                    {
                        "skill": s,
                        "description": f"Master foundational fundamentals and syntax of {s}.",
                        "resources": f"Official documentation and tutorials for {s}",
                        "est_hours": 10
                    }
                    for s in (missing_skills[:2] or ["Programming Fundamentals"])
                ]
            },
            {
                "title": "Phase 2: Core Competencies",
                "order": 2,
                "items": [
                    {
                        "skill": s.split()[0],
                        "description": f"Apply {s} in practical projects and real-world architectures.",
                        "resources": f"Coursera / YouTube Guided Projects for {s}",
                        "est_hours": 18
                    }
                    for s in (partial_skills[:2] or missing_skills[2:4] or ["Core Development"])
                ]
            },
            {
                "title": "Phase 3: Advanced & Capstone",
                "order": 3,
                "items": [
                    {
                        "skill": "Full Portfolio Integration & Mock Interview",
                        "description": "Build an end-to-end capstone application demonstrating all required competencies.",
                        "resources": "GitHub Projects & System Design Handbook",
                        "est_hours": 20
                    }
                ]
            }
        ]

    for p_idx, phase_info in enumerate(phases_data, start=1):
        phase_title = phase_info.get("title", f"Phase {p_idx}")
        order = phase_info.get("order", p_idx)
        phase_obj = Phase.objects.create(
            roadmap=roadmap,
            title=phase_title,
            order=order
        )

        for item_info in phase_info.get("items", []):
            RoadmapItem.objects.create(
                phase=phase_obj,
                skill=item_info.get("skill", "Core Skill"),
                description=item_info.get("description", ""),
                resources=item_info.get("resources", ""),
                est_hours=int(item_info.get("est_hours", 10)),
                status="todo"
            )

    return roadmap
