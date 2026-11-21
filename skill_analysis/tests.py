import io
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import (
    Resume, JobDescription, Analysis, Skill, AnalysisSkill,
    SkillGap, Roadmap, Phase, RoadmapItem, Message
)
from .services.ingestion import clean_text, clean_job_description, extract_text_from_pdf
from .services.extractor import normalize_skill_name, process_and_store_skills
from .services.embeddings import get_embedding, cosine_similarity, compute_skill_similarity
from .services.gap_analyzer import run_gap_analysis
from .services.roadmap_generator import generate_roadmap_for_analysis
from .services.assistant import answer_user_query
from .services.llm import strip_fences


class Module1IngestionTests(TestCase):
    def test_clean_text_normalizes_bullets_and_whitespace(self):
        raw = "• Python programming\n\n\n\n*   Django development \t with Docker"
        cleaned = clean_text(raw)
        self.assertIn("- Python programming", cleaned)
        self.assertIn("- Django development with Docker", cleaned)
        self.assertNotIn("\t", cleaned)

    def test_clean_job_description_validation(self):
        short_jd = "Short"
        with self.assertRaises(ValueError):
            clean_job_description(short_jd)

        valid_jd = "We are seeking a Full Stack Software Engineer proficient in Python, Django, React, and PostgreSQL."
        cleaned = clean_job_description(valid_jd)
        self.assertEqual(cleaned, valid_jd)

    def test_empty_or_scanned_pdf_rejection(self):
        # Empty byte stream should be rejected with friendly ValueError
        empty_buffer = io.BytesIO(b"%PDF-1.4 empty content")
        with self.assertRaises(ValueError) as ctx:
            extract_text_from_pdf(empty_buffer)
        self.assertTrue("PDF" in str(ctx.exception) or "readable" in str(ctx.exception))


class Module2SkillExtractionTests(TestCase):
    def test_skill_normalization_and_aliases(self):
        self.assertEqual(normalize_skill_name("JS"), "javascript")
        self.assertEqual(normalize_skill_name("Postgres"), "postgresql")
        self.assertEqual(normalize_skill_name("React.js"), "react")
        self.assertEqual(normalize_skill_name("k8s"), "kubernetes")
        self.assertEqual(normalize_skill_name("  C++  "), "c++")
        self.assertEqual(normalize_skill_name("C#"), "c#")

    def test_process_and_store_skills(self):
        resume = Resume.objects.create(
            extracted_text="Experienced in Python, Django, PostgreSQL, Git, and Docker.",
            file_type="pdf"
        )
        jd = JobDescription.objects.create(
            title="Backend Developer",
            text="Must have Python, Django, PostgreSQL, and Kubernetes (k8s)."
        )
        analysis = Analysis.objects.create(resume=resume, jd=jd)

        res_skills, jd_skills = process_and_store_skills(analysis)
        self.assertTrue(len(res_skills) > 0)
        self.assertTrue(len(jd_skills) > 0)

        # Check that normalized skills were stored
        skill_names = [s.skill.name for s in res_skills]
        self.assertIn("python", skill_names)


class Module3GapDetectionTests(TestCase):
    def setUp(self):
        self.resume = Resume.objects.create(
            extracted_text="Python, Django, SQL, Git",
            file_type="pdf"
        )
        self.jd = JobDescription.objects.create(
            title="Python Developer",
            text="Required: Python, Django. Nice to have: Kubernetes"
        )
        self.analysis = Analysis.objects.create(resume=self.resume, jd=self.jd)

        # Populate skills directly for deterministic gap testing
        s_python, _ = Skill.objects.get_or_create(name="python")
        s_django, _ = Skill.objects.get_or_create(name="django")
        s_k8s, _ = Skill.objects.get_or_create(name="kubernetes")

        AnalysisSkill.objects.create(analysis=self.analysis, skill=s_python, source='resume')
        AnalysisSkill.objects.create(analysis=self.analysis, skill=s_django, source='resume')

        AnalysisSkill.objects.create(analysis=self.analysis, skill=s_python, source='jd', importance='required')
        AnalysisSkill.objects.create(analysis=self.analysis, skill=s_django, source='jd', importance='required')
        AnalysisSkill.objects.create(analysis=self.analysis, skill=s_k8s, source='jd', importance='nice_to_have')

    def test_run_gap_analysis(self):
        results = run_gap_analysis(self.analysis)
        self.analysis.refresh_from_db()

        self.assertGreater(results["match_score"], 0)
        self.assertEqual(results["matched_count"], 2) # python, django
        self.assertEqual(results["missing_count"], 1) # kubernetes

        gaps = SkillGap.objects.filter(analysis=self.analysis)
        self.assertEqual(gaps.count(), 3)
        py_gap = gaps.get(jd_skill__name="python")
        self.assertEqual(py_gap.status, "matched")
        self.assertGreaterEqual(py_gap.similarity, 0.80)


class Module4RoadmapGenerationTests(TestCase):
    def test_roadmap_generation(self):
        resume = Resume.objects.create(extracted_text="Python, HTML", file_type="pdf")
        jd = JobDescription.objects.create(title="Fullstack Developer", text="Python, React, AWS")
        analysis = Analysis.objects.create(resume=resume, jd=jd)

        s_py, _ = Skill.objects.get_or_create(name="python")
        s_react, _ = Skill.objects.get_or_create(name="react")
        s_aws, _ = Skill.objects.get_or_create(name="aws")

        SkillGap.objects.create(analysis=analysis, jd_skill=s_py, status="matched", similarity=1.0)
        SkillGap.objects.create(analysis=analysis, jd_skill=s_react, status="missing", similarity=0.2)
        SkillGap.objects.create(analysis=analysis, jd_skill=s_aws, status="partial", similarity=0.65)

        roadmap = generate_roadmap_for_analysis(analysis)
        self.assertIsNotNone(roadmap)
        self.assertEqual(roadmap.phases.count(), 3)
        self.assertGreater(RoadmapItem.objects.filter(phase__roadmap=roadmap).count(), 0)


class Module5ProgressTrackingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.resume = Resume.objects.create(extracted_text="Python", file_type="pdf")
        self.jd = JobDescription.objects.create(title="Dev", text="Python")
        self.analysis = Analysis.objects.create(resume=self.resume, jd=self.jd)
        self.roadmap = Roadmap.objects.create(analysis=self.analysis)
        self.phase = Phase.objects.create(roadmap=self.roadmap, title="Phase 1", order=1)
        self.item1 = RoadmapItem.objects.create(phase=self.phase, skill="Skill 1", est_hours=10, status="todo")
        self.item2 = RoadmapItem.objects.create(phase=self.phase, skill="Skill 2", est_hours=20, status="todo")

    def test_progress_calculation(self):
        self.assertEqual(self.phase.progress_percentage(), 0)
        self.assertEqual(self.roadmap.overall_progress_percentage(), 0)

        # Mark item1 as done (10 hours out of 30 total hours = 33%)
        self.item1.status = "done"
        self.item1.save()

        self.assertEqual(self.phase.progress_percentage(), 50) # 1 of 2 items
        self.assertEqual(self.roadmap.overall_progress_percentage(), 33) # 10 / 30 hours

    def test_htmx_status_update_endpoint(self):
        url = reverse("skill_analysis:update_roadmap_item_status", args=[self.item1.id])
        response = self.client.post(url, {"status": "done"}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.status, "done")
        self.assertContains(response, "Completed")


class Module7AIAssistantTests(TestCase):
    def test_assistant_interaction_and_continuity(self):
        resume = Resume.objects.create(extracted_text="Python", file_type="pdf")
        jd = JobDescription.objects.create(title="Software Engineer", text="Python")
        analysis = Analysis.objects.create(resume=resume, jd=jd, match_score=75.0)

        reply = answer_user_query(analysis, "How can I prepare for the interview?")
        self.assertTrue(len(reply) > 0)

        # Ensure both user message and assistant reply are saved
        messages = Message.objects.filter(analysis=analysis)
        self.assertEqual(messages.count(), 2)
        self.assertEqual(messages.first().role, "user")
        self.assertEqual(messages.last().role, "assistant")


class Module8SharedServicesTests(TestCase):
    def test_strip_fences(self):
        fenced = "```json\n{\"test\": 123}\n```"
        self.assertEqual(strip_fences(fenced), '{"test": 123}')

    def test_cosine_similarity_and_caching(self):
        v1 = [1.0, 0.0, 0.0]
        v2 = [1.0, 0.0, 0.0]
        v3 = [0.0, 1.0, 0.0]
        self.assertAlmostEqual(cosine_similarity(v1, v2), 1.0)
        self.assertAlmostEqual(cosine_similarity(v1, v3), 0.0)

        # Test embedding retrieval & caching
        emb1 = get_embedding("python")
        emb2 = get_embedding("python")
        self.assertEqual(emb1, emb2)
        self.assertGreater(len(emb1), 0)

        # Similarity between identical skills should be 1.0
        self.assertEqual(compute_skill_similarity("python", "python"), 1.0)


class Module6ViewsIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_dashboard_view(self):
        url = reverse("skill_analysis:dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Resume & Skill Gap Analysis")

    def test_analysis_creation_flow(self):
        # Create a sample text file pretending to be resume docx
        fake_pdf = SimpleUploadedFile(
            "sample_resume.pdf",
            b"%PDF-1.4 sample resume content for python django postgresql docker git engineer",
            content_type="application/pdf"
        )
        url = reverse("skill_analysis:create_analysis")
        # Empty or short JD should trigger error redirect
        res = self.client.post(url, {
            "title": "Backend Dev",
            "resume_file": fake_pdf,
            "jd_text": "Short"
        }, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Please provide a detailed job description")
