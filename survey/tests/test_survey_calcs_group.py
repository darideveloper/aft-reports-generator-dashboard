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

    def create_final_report(self, total: float = 50.0) -> survey_models.Report:
        """
        Create a single report

        Args:
            total (float): The total to set for the report

        Returns:
            survey_models.Report: The created report
        """

        participant = self.create_participant(company=self.company)
        report = survey_models.Report.objects.create(
            participant=participant, survey=self.survey, total=total
        )
        return report

    def create_final_reports(self, total: float = 50.0, count: int = 100):
        """
        Create reports with total

        Args:
            total (float): The total to set for the reports
            count (int): The number of reports to create
        """

        for _ in range(count):
            self.create_final_report(total=total)

    def test_get_employees_number(self):
        """Validate correct count of reports"""

        # initialize data
        self.create_final_reports(count=50)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # Valdiate num
        self.assertEqual(calcs.get_employees_number(), 50)

    def test_get_average_score_0(self):
        """Validate average number when all reports have 0 total"""

        # initialize data
        self.create_final_reports(count=50, total=0.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # Validate average
        self.assertEqual(calcs.get_average_num(), 0)

    def test_get_average_score_50(self):
        """Validate average number when all reports have 50 total"""

        # initialize data
        self.create_final_reports(count=50, total=50.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average
        self.assertEqual(calcs.get_average_num(), 50.0)

    def test_get_average_score_100(self):
        """Validate average number when all reports have 50 total"""

        # initialize data
        self.create_final_reports(count=50, total=100.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average
        self.assertEqual(calcs.get_average_num(), 100.0)

    def test_get_average_employees_0(self):
        """Validate average number when all reports have 50 total"""

        # initialize data
        self.create_final_reports(count=0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average
        self.assertEqual(calcs.get_average_num(), 0.0)

    def test_get_average_range_0(self):
        """Validate average range when all reports have 0 total (low range)"""

        # initialize data
        self.create_final_reports(count=50, total=0.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "low")

    def test_get_average_range_59(self):
        """Validate average range when all reports have 59 total (low range)"""

        # initialize data
        self.create_final_reports(count=50, total=59.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "low")

    def test_get_average_range_60(self):
        """Validate average range when all reports have 59 total (low range)"""

        # initialize data
        self.create_final_reports(count=50, total=60.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "medium")

    def test_get_average_range_79(self):
        """Validate average range when all reports have 59 total (low range)"""

        # initialize data
        self.create_final_reports(count=50, total=79.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "medium")

    def test_get_average_range_80(self):
        """Validate average range when all reports have 59 total (low range)"""

        # initialize data
        self.create_final_reports(count=50, total=80.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "high")

    def test_get_average_range_100(self):
        """Validate average range when all reports have 59 total (low range)"""

        # initialize data
        self.create_final_reports(count=50, total=100.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "high")
