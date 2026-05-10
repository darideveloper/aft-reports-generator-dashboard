import os
from django.core.management import call_command
from rest_framework.test import APITestCase
from survey.tests.test_commands import GenerateNextReportBase
from survey import models as survey_models
from utils.survey_calcs_group import SurveyCalcsGroup
from utils.survey_calcs import SurveyCalcs

class TestSurveyCalcsGroupOrdered(GenerateNextReportBase):
    """
    Test cases for get_average_areas_ordered method in SurveyCalcsGroup
    """

    def test_get_average_areas_ordered_question_groups(self):
        """
        Test calculating and ordering average scores for question groups
        """
        # Create a second participant and report
        participant2 = self.create_participant(company=self.company, email="test2@example.com")
        report2 = survey_models.Report.objects.create(
            participant=participant2,
            survey=self.survey,
            status="completed"
        )

        # First report already created in setUp (implicitly)
        # We need to ensure the first report is also set up correctly
        report1 = survey_models.Report.objects.filter(participant=self.participant).first()
        if not report1:
             report1 = survey_models.Report.objects.create(
                participant=self.participant,
                survey=self.survey,
                status="completed"
            )

        # Create scores for QuestionGroup 1
        qg1 = self.question_groups[0]
        survey_models.ReportQuestionGroupTotal.objects.create(report=report1, question_group=qg1, total=80)
        survey_models.ReportQuestionGroupTotal.objects.create(report=report2, question_group=qg1, total=90)
        # Average QG1 = 85

        # Create scores for QuestionGroup 2
        qg2 = self.question_groups[1]
        survey_models.ReportQuestionGroupTotal.objects.create(report=report1, question_group=qg2, total=60)
        survey_models.ReportQuestionGroupTotal.objects.create(report=report2, question_group=qg2, total=40)
        # Average QG2 = 50

        reports = survey_models.Report.objects.filter(participant__company=self.company)
        calcs = SurveyCalcsGroup(reports=reports)
        ordered_areas = calcs.get_average_areas_ordered(use_summary=False)

        self.assertEqual(len(ordered_areas), 2)
        self.assertEqual(ordered_areas[0]["area"], qg1)
        self.assertEqual(ordered_areas[0]["average"], 85.0)
        self.assertEqual(ordered_areas[1]["area"], qg2)
        self.assertEqual(ordered_areas[1]["average"], 50.0)

    def test_get_average_areas_ordered_summary(self):
        """
        Test calculating and ordering average scores for summary categories
        """
        participant2 = self.create_participant(company=self.company, email="test2@example.com")
        report2 = survey_models.Report.objects.create(
            participant=participant2,
            survey=self.survey,
            status="completed"
        )
        report1 = survey_models.Report.objects.filter(participant=self.participant).first()
        if not report1:
             report1 = survey_models.Report.objects.create(
                participant=self.participant,
                survey=self.survey,
                status="completed"
            )

        # Category CD
        survey_models.ReportSummaryScore.objects.create(report=report1, paragraph_type="CD", score=70)
        survey_models.ReportSummaryScore.objects.create(report=report2, paragraph_type="CD", score=80)
        # Average CD = 75

        # Category CS
        survey_models.ReportSummaryScore.objects.create(report=report1, paragraph_type="CS", score=90)
        survey_models.ReportSummaryScore.objects.create(report=report2, paragraph_type="CS", score=100)
        # Average CS = 95

        reports = survey_models.Report.objects.filter(participant__company=self.company)
        calcs = SurveyCalcsGroup(reports=reports)
        ordered_areas = calcs.get_average_areas_ordered(use_summary=True)

        self.assertEqual(len(ordered_areas), 2)
        self.assertEqual(ordered_areas[0]["area"], "CS")
        self.assertEqual(ordered_areas[0]["average"], 95.0)
        self.assertEqual(ordered_areas[1]["area"], "CD")
        self.assertEqual(ordered_areas[1]["average"], 75.0)

    def test_get_average_areas_ordered_empty(self):
        """
        Test handling of empty reports queryset
        """
        reports = survey_models.Report.objects.filter(id=99999) # Empty
        calcs = SurveyCalcsGroup(reports=reports)
        ordered_areas = calcs.get_average_areas_ordered()
        self.assertEqual(ordered_areas, [])
