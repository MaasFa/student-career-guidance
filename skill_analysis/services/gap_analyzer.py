import logging
from typing import Dict, Any, List
from skill_analysis.models import Analysis, AnalysisSkill, SkillGap, Skill
from skill_analysis.services.embeddings import compute_skill_similarity

logger = logging.getLogger(__name__)

SIMILARITY_MATCHED_THRESHOLD = 0.80
SIMILARITY_PARTIAL_THRESHOLD = 0.55


def run_gap_analysis(analysis: Analysis) -> Dict[str, Any]:
    """
    Computes semantic gap between resume skills and JD skills.
    Creates or updates SkillGap records and computes weighted match score.
    """
    resume_skills = list(
        AnalysisSkill.objects.filter(analysis=analysis, source='resume').select_related('skill')
    )
    jd_skills = list(
        AnalysisSkill.objects.filter(analysis=analysis, source='jd').select_related('skill')
    )

    if not jd_skills:
        logger.warning(f"No JD skills found for analysis #{analysis.id}.")
        analysis.match_score = 0.0
        analysis.save(update_fields=['match_score'])
        return {
            "match_score": 0.0,
            "matched_count": 0,
            "partial_count": 0,
            "missing_count": 0,
            "gaps": []
        }

    # Delete existing gaps for re-analysis
    SkillGap.objects.filter(analysis=analysis).delete()

    total_weight = 0.0
    earned_weight = 0.0
    matched_count = 0
    partial_count = 0
    missing_count = 0
    created_gaps = []

    for jd_item in jd_skills:
        jd_skill = jd_item.skill
        importance = jd_item.importance

        # Weight factor: required skills carry double weight compared to nice_to_have
        weight = 2.0 if importance == 'required' else 1.0
        total_weight += weight

        best_similarity = 0.0
        closest_resume_skill = None

        for res_item in resume_skills:
            res_skill = res_item.skill
            sim = compute_skill_similarity(jd_skill.name, res_skill.name)
            if sim > best_similarity:
                best_similarity = sim
                closest_resume_skill = res_skill

        # Determine status according to thresholds
        if best_similarity >= SIMILARITY_MATCHED_THRESHOLD:
            status = 'matched'
            earned_weight += (1.0 * weight)
            matched_count += 1
        elif best_similarity >= SIMILARITY_PARTIAL_THRESHOLD:
            status = 'partial'
            # Partial credit proportional to similarity
            earned_weight += (best_similarity * weight)
            partial_count += 1
        else:
            status = 'missing'
            # No credit
            closest_resume_skill = None
            missing_count += 1

        gap = SkillGap.objects.create(
            analysis=analysis,
            jd_skill=jd_skill,
            closest_resume_skill=closest_resume_skill,
            similarity=round(best_similarity, 3),
            status=status
        )
        created_gaps.append(gap)

    # Compute final percentage score
    final_score = round((earned_weight / total_weight) * 100, 1) if total_weight > 0 else 0.0
    analysis.match_score = final_score
    analysis.save(update_fields=['match_score'])

    return {
        "match_score": final_score,
        "matched_count": matched_count,
        "partial_count": partial_count,
        "missing_count": missing_count,
        "total_jd_skills": len(jd_skills),
        "gaps": created_gaps
    }
