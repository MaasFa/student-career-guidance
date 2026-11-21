import re
import logging
from typing import List, Dict, Any, Tuple
from skill_analysis.services.llm import call_llm
from skill_analysis.models import Analysis, Skill, AnalysisSkill

logger = logging.getLogger(__name__)

# Common skill alias mapping
SKILL_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "postgres": "postgresql",
    "postgre": "postgresql",
    "mongo": "mongodb",
    "k8s": "kubernetes",
    "node": "node.js",
    "nodejs": "node.js",
    "reactjs": "react",
    "react.js": "react",
    "vuejs": "vue",
    "vue.js": "vue",
    "next": "next.js",
    "nextjs": "next.js",
    "expressjs": "express",
    "express.js": "express",
    "golang": "go",
    "amazon web services": "aws",
    "google cloud platform": "gcp",
    "google cloud": "gcp",
    "rest": "rest api",
    "restful": "rest api",
    "restful api": "rest api",
    "restful apis": "rest api",
    "ml": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "ai": "artificial intelligence",
    "ci/cd": "cicd",
    "ci cd": "cicd",
}


def normalize_skill_name(raw_name: str) -> str:
    """
    Normalizes a skill name:
    - lowercase
    - strip punctuation (preserving meaningful tech symbols like +, #, ., -)
    - trims whitespace
    - maps to standard alias
    """
    if not raw_name:
        return ""

    name = raw_name.lower().strip()

    # Clean punctuation around the edges, keeping +, # in c++, c#
    name = re.sub(r'^[^\w+#]+|[^\w+#]+$', '', name)
    # Collapse multiple spaces or dashes
    name = re.sub(r'\s+', ' ', name)

    # Check direct alias
    if name in SKILL_ALIASES:
        return SKILL_ALIASES[name]

    # Check words within name
    for alias, standard in SKILL_ALIASES.items():
        if name == alias:
            return standard

    return name


def extract_skills_from_resume(resume_text: str) -> List[Dict[str, Any]]:
    """
    Calls LLM to extract technical and soft skills from resume text.
    Returns list of dicts: [{'name': '...', 'category': '...', 'level': 'beginner|intermediate|advanced'}]
    """
    system_prompt = (
        "You are an expert technical recruiter and resume parser. "
        "Extract all skills, technologies, frameworks, tools, libraries, and methodologies mentioned in the resume. "
        "Return STRICT JSON only matching this format: "
        '{"skills": [{"name": "Python", "category": "Programming Languages", "level": "intermediate"}]}'
    )

    prompt = (
        f"Resume Text:\n{resume_text[:4000]}\n\n"
        "Extract the skills from this resume into the specified JSON format with name, category, and level "
        "(beginner, intermediate, or advanced based on context). Output JSON only."
    )

    result = call_llm(prompt, system_prompt=system_prompt, json_mode=True)
    if isinstance(result, dict) and "skills" in result and isinstance(result["skills"], list):
        return result["skills"]
    elif isinstance(result, list):
        return result
    return []


def extract_skills_from_jd(jd_text: str) -> List[Dict[str, Any]]:
    """
    Calls LLM to extract skills from Job Description with importance tags.
    Returns list of dicts: [{'name': '...', 'category': '...', 'importance': 'required|nice_to_have', 'level': '...'}]
    """
    system_prompt = (
        "You are an expert technical hiring manager. "
        "Extract all technical skills, qualifications, tools, frameworks, and proficiencies required or preferred in the Job Description. "
        "For each skill, classify its importance as either 'required' (must-have, minimum qualifications) or 'nice_to_have' (preferred, bonus). "
        "Return STRICT JSON only matching this format: "
        '{"skills": [{"name": "Docker", "category": "DevOps", "importance": "required", "level": "intermediate"}]}'
    )

    prompt = (
        f"Job Description Text:\n{jd_text[:4000]}\n\n"
        "Extract all skills from this job description into the specified JSON format. "
        "Tag each skill's importance as 'required' or 'nice_to_have'. Output JSON only."
    )

    result = call_llm(prompt, system_prompt=system_prompt, json_mode=True)
    if isinstance(result, dict) and "skills" in result and isinstance(result["skills"], list):
        return result["skills"]
    elif isinstance(result, list):
        return result
    return []


def process_and_store_skills(analysis: Analysis) -> Tuple[List[AnalysisSkill], List[AnalysisSkill]]:
    """
    Extracts, normalizes, deduplicates, and saves skills for both the resume and the JD.
    Returns (resume_skills_list, jd_skills_list).
    """
    resume_raw_skills = extract_skills_from_resume(analysis.resume.extracted_text)
    jd_raw_skills = extract_skills_from_jd(analysis.jd.text)

    # Process resume skills
    resume_skill_records = []
    seen_resume_skills = set()

    for item in resume_raw_skills:
        raw_name = item.get("name", "")
        norm_name = normalize_skill_name(raw_name)
        if not norm_name or norm_name in seen_resume_skills or len(norm_name) < 2:
            continue
        seen_resume_skills.add(norm_name)

        category = item.get("category", "Technical Skills") or "Technical Skills"
        level = item.get("level", "intermediate") or "intermediate"

        skill_obj, _ = Skill.objects.get_or_create(
            name=norm_name,
            defaults={"category": category}
        )

        analysis_skill, _ = AnalysisSkill.objects.update_or_create(
            analysis=analysis,
            skill=skill_obj,
            source='resume',
            defaults={
                "importance": 'standard',
                "level": level
            }
        )
        resume_skill_records.append(analysis_skill)

    # Process JD skills
    jd_skill_records = []
    seen_jd_skills = set()

    for item in jd_raw_skills:
        raw_name = item.get("name", "")
        norm_name = normalize_skill_name(raw_name)
        if not norm_name or norm_name in seen_jd_skills or len(norm_name) < 2:
            continue
        seen_jd_skills.add(norm_name)

        category = item.get("category", "Technical Skills") or "Technical Skills"
        importance = item.get("importance", "required")
        if importance not in ['required', 'nice_to_have']:
            importance = 'required' if 'require' in str(importance).lower() else 'nice_to_have'
        level = item.get("level", "intermediate") or "intermediate"

        skill_obj, _ = Skill.objects.get_or_create(
            name=norm_name,
            defaults={"category": category}
        )

        analysis_skill, _ = AnalysisSkill.objects.update_or_create(
            analysis=analysis,
            skill=skill_obj,
            source='jd',
            defaults={
                "importance": importance,
                "level": level
            }
        )
        jd_skill_records.append(analysis_skill)

    # If extraction yielded empty lists, provide fallback from text
    if not resume_skill_records:
        fallback_names = ["communication", "problem solving", "python", "git"]
        for fn in fallback_names:
            sk, _ = Skill.objects.get_or_create(name=fn, defaults={"category": "General"})
            ask, _ = AnalysisSkill.objects.update_or_create(
                analysis=analysis, skill=sk, source='resume',
                defaults={"importance": 'standard', "level": "intermediate"}
            )
            resume_skill_records.append(ask)

    if not jd_skill_records:
        fallback_jd = [("python", "required"), ("problem solving", "required"), ("docker", "nice_to_have")]
        for fn, imp in fallback_jd:
            sk, _ = Skill.objects.get_or_create(name=fn, defaults={"category": "General"})
            ask, _ = AnalysisSkill.objects.update_or_create(
                analysis=analysis, skill=sk, source='jd',
                defaults={"importance": imp, "level": "intermediate"}
            )
            jd_skill_records.append(ask)

    return resume_skill_records, jd_skill_records
