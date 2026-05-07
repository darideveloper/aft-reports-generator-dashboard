from core.tests_base.test_models import TestSurveyModelBase
from django.core.management import call_command
from survey import models as survey_models
from utils.survey_calcs_group import SurveyCalcsGroup


class SurveyCalcsGroupTestCase(TestSurveyModelBase):
    def setUp(self):
        # Intiial setup
        super().setUp()
        call_command("apps_loaddata")
        call_command("initial_loaddata")
        self.company = self.create_company()
        self.survey = survey_models.Survey.objects.get(id=1)

        # Create 50 random reports
        self.reports = []
        for _ in range(50):
            self.reports.append(self.create_report())

        # initialize calcs
        self.calcs = SurveyCalcsGroup(self.reports)

    def create_report(self) -> survey_models.Report:
        """
        Create a single report

        Returns:
            survey_models.Report: The created report
        """
        participant = self.create_participant(company=self.company)
        report = survey_models.Report.objects.create(
            participant=participant, survey=self.survey, total=50.0
        )
        return report

    def test_get_employees_number(self):
        self.assertEqual(self.calcs.get_employees_number(), 50)
