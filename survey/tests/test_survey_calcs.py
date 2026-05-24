from django.test import TestCase
from survey import models as survey_models
from utils.survey_calcs import SurveyCalcs
from core.tests_base.test_models import TestSurveyModelBase
from django.core.management import call_command

class SurveyCalcsUnitTestCase(TestSurveyModelBase):
    def setUp(self):
        super().setUp()
        call_command("apps_loaddata")
        call_command("initial_loaddata")
        self.company = self.create_company()
        self.participant = self.create_participant(company=self.company)
        self.survey = survey_models.Survey.objects.get(id=1)
        # We don't use create_report here to avoid automatic triggers
        self.report = survey_models.Report.objects.create(
            participant=self.participant,
            survey=self.survey,
            total=50.0
        )
        self.calcs = SurveyCalcs(self.participant, self.survey, self.report)

    def test_save_report_summary_scores_averaging(self):
        # Setup specific mapping for CD
        qg1 = survey_models.QuestionGroup.objects.get(survey_index=1)
        qg2 = survey_models.QuestionGroup.objects.get(survey_index=2)
        summary_cd = survey_models.TextPDFSummary.objects.filter(paragraph_type="CD").first()
        summary_cd.question_groups.set([qg1, qg2])

        # Create topic scores
        survey_models.ReportQuestionGroupTotal.objects.create(report=self.report, question_group=qg1, total=80.0)
        survey_models.ReportQuestionGroupTotal.objects.create(report=self.report, question_group=qg2, total=40.0)

        self.calcs.save_report_summary_scores()

        score_record = survey_models.ReportSummaryScore.objects.get(report=self.report, paragraph_type="CD")
        self.assertEqual(score_record.score, 60.0)

    def test_save_report_summary_scores_rounding(self):
        qg1 = survey_models.QuestionGroup.objects.get(survey_index=1)
        qg2 = survey_models.QuestionGroup.objects.get(survey_index=2)
        qg3 = survey_models.QuestionGroup.objects.get(survey_index=3)
        summary_cd = survey_models.TextPDFSummary.objects.filter(paragraph_type="CD").first()
        summary_cd.question_groups.set([qg1, qg2, qg3])

        # (80 + 40 + 41) / 3 = 161 / 3 = 53.666...
        survey_models.ReportQuestionGroupTotal.objects.create(report=self.report, question_group=qg1, total=80.0)
        survey_models.ReportQuestionGroupTotal.objects.create(report=self.report, question_group=qg2, total=40.0)
        survey_models.ReportQuestionGroupTotal.objects.create(report=self.report, question_group=qg3, total=41.0)

        self.calcs.save_report_summary_scores()

        score_record = survey_models.ReportSummaryScore.objects.get(report=self.report, paragraph_type="CD")
        self.assertEqual(score_record.score, 53.67)

    def test_get_resulting_titles_selection_logic(self):
        # Create manual summary score: 80.0
        survey_models.ReportSummaryScore.objects.create(report=self.report, paragraph_type="CD", score=80.0)
        
        # Setup thresholds: 100.0 (Max), 79.0 (Intermediate), 49.0 (Low)
        survey_models.TextPDFSummary.objects.filter(paragraph_type="CD").delete()
        survey_models.TextPDFSummary.objects.create(
            paragraph_type="CD", min_score=100.0, text="Max Title | Max Text"
        )
        survey_models.TextPDFSummary.objects.create(
            paragraph_type="CD", min_score=79.0, text="Intermediate Title | Intermediate Text"
        )
        survey_models.TextPDFSummary.objects.create(
            paragraph_type="CD", min_score=49.0, text="Low Title | Low Text"
        )

        # Test Case 1: Score 80.0 -> Should match 100.0 (smallest threshold >= 80)
        titles = self.calcs.get_resulting_titles()
        self.assertEqual(titles["cd"]["subtitle"], "Max Title")

        # Test Case 2: Score 50.0 -> Should match 79.0 (smallest threshold >= 50)
        score_record = survey_models.ReportSummaryScore.objects.get(report=self.report, paragraph_type="CD")
        score_record.score = 50.0
        score_record.save()
        titles = self.calcs.get_resulting_titles()
        self.assertEqual(titles["cd"]["subtitle"], "Intermediate Title")

        # Test Case 3: Score 40.0 -> Should match 49.0 (smallest threshold >= 40)
        score_record.score = 40.0
        score_record.save()
        titles = self.calcs.get_resulting_titles()
        self.assertEqual(titles["cd"]["subtitle"], "Low Title")

        # Test Case 4: Score 110.0 -> Should fallback to highest (100.0)
        score_record.score = 110.0
        score_record.save()
        titles = self.calcs.get_resulting_titles()
        self.assertEqual(titles["cd"]["subtitle"], "Max Title")

    def test_edge_case_no_mapped_topics(self):
        # Category CS has no topics mapped in this test setup (if we don't set them)
        # It should fallback to report.total (which is 50.0 in setUp)
        summary_cs = survey_models.TextPDFSummary.objects.filter(paragraph_type="CS").first()
        summary_cs.question_groups.clear()

        self.calcs.save_report_summary_scores()

        score_record = survey_models.ReportSummaryScore.objects.get(report=self.report, paragraph_type="CS")
        self.assertEqual(score_record.score, 50.0)

    def test_edge_case_missing_topic_scores(self):
        # Mapped topics exist but no ReportQuestionGroupTotal records
        qg1 = survey_models.QuestionGroup.objects.get(survey_index=1)
        summary_cd = survey_models.TextPDFSummary.objects.filter(paragraph_type="CD").first()
        summary_cd.question_groups.set([qg1])
        
        # Ensure no score record exists
        survey_models.ReportQuestionGroupTotal.objects.filter(report=self.report, question_group=qg1).delete()

        self.calcs.save_report_summary_scores()

        score_record = survey_models.ReportSummaryScore.objects.get(report=self.report, paragraph_type="CD")
        self.assertEqual(score_record.score, 0)

    def test_get_company_average(self):
        self.report.total = 80.0
        self.report.save()
        
        participant2 = survey_models.Participant.objects.create(
            company=self.company,
            name="Test User 2",
            email="test2@example.com"
        )
        survey_models.Report.objects.create(
            participant=participant2,
            survey=self.survey,
            total=60.0
        )
        
        self.assertEqual(self.calcs.get_company_average(), 70.0)

    def test_get_global_average(self):
        self.report.total = 90.0
        self.report.save()

        company2 = survey_models.Company.objects.create(name="Other Company")
        participant2 = survey_models.Participant.objects.create(
            company=company2,
            name="Other User",
            email="other@example.com"
        )
        survey_models.Report.objects.create(
            participant=participant2,
            survey=self.survey,
            total=70.0
        )

        self.assertEqual(self.calcs.get_global_average(), 80.0)
