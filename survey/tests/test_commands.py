from core.tests_base.test_models import TestSurveyModelBase
from django.core.management import call_command

from survey import models as survey_models

from utils.media import get_media_url


class GenerateNextReportCommandTestCase(TestSurveyModelBase):
    """Test generate next report command"""

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Create 3 recports with default status
        self.company = self.create_company()
        self.survey = self.create_survey()
        self.participant = self.create_participant(company=self.company)
        self.reports = []
        for _ in range(3):
            self.reports.append(
                self.create_report(survey=self.survey, participant=self.participant)
            )
            
    def __validate_report(self, report: survey_models.Report):
        """Validate report data
        
        Args:
            report (survey_models.Report): The report to validate
        """
        
        # Update report data
        report.refresh_from_db()
        
        # Validate status
        self.assertEqual(report.status, "completed")
        self.assertIsNotNone(report.pdf_file)
        
        # Validate url is a valid .pdf link
        pdf_url = get_media_url(report.pdf_file)
        self.assertTrue(pdf_url.endswith(".pdf"))
        
        # TODO: test cacls

    def test_many_pending_reports(self):
        """Test with many pending reports
        Expect:
            - The command should update the status of the report to completed
        """

        call_command("generate_next_report")

        # Validate report data
        self.__validate_report(self.reports[0])

        # Validate other reports are still pending
        for other_report in self.reports[1:]:
            other_report.refresh_from_db()
            self.assertEqual(other_report.status, "pending")

    def test_single_report(self):
        """Test with a single report
        Expect:
            - The command should update the status of the report to completed
        """
        
        # Delete other reports
        for report in self.reports[1:]:
            report.delete()
        
        call_command("generate_next_report")
        
        # Validate report data
        self.__validate_report(self.reports[0])

    def test_no_pending_reports(self):
        """Test with no pending reports
        Expect:
            - The command should do nothing (skip all reports)
        """

        # Set all reports to completed
        for report in self.reports:
            report.status = "processing"
            report.save()

        call_command("generate_next_report")

        # Validate no reports are ready to be processed or completed
        self.assertEqual(
            survey_models.Report.objects.filter(status="pending").count(), 0
        )
        self.assertEqual(
            survey_models.Report.objects.filter(status="completed").count(), 0
        )
        self.assertEqual(
            survey_models.Report.objects.filter(status="error").count(), 0
        )
        
 