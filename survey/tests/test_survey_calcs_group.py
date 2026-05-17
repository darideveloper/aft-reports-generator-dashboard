import random

from core.tests_base.test_models import TestSurveyModelBase
from django.core.management import call_command
from survey import models as survey_models
from utils.survey_calcs_group import SurveyCalcsGroup
from django.contrib.auth.models import User


class SurveyCalcsGroupTestCase(TestSurveyModelBase):
    def setUp(self):
        # Intiial setup and initial data
        super().setUp()
        call_command("apps_loaddata")
        call_command("initial_loaddata")
        self.company = self.create_company()
        self.survey = survey_models.Survey.objects.get(id=1)
        self.questions, self.options = self.create_question_and_options()

        # Login to client with session
        username = "test_user"
        password = "test_pass"
        User.objects.create_superuser(
            username=username,
            email="test@gmail.com",
            password=password,
        )
        self.client.login(username=username, password=password)

    def create_final_reports(
        self, total: float = 50.0, count: int = 100, total_random: bool = False
    ):
        """
        Create reports with total

        Args:
            total (float): The total to set for the reports
            count (int): The number of reports to create
            total_random (bool): Whether to get random score (override total)
        """

        reports = []
        for _ in range(count):
            options = self.get_selected_options(score=total, random_score=total_random)
            report = self.create_report(options=options)
            reports.append(report)

        return reports

    def test_get_employees_number(self):
        """Validate correct count of reports"""

        # initialize data
        self.create_final_reports(count=10)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # Valdiate num
        self.assertEqual(calcs.get_employees_number(), 10)

    def test_get_average_score_0(self):
        """Validate average number when all reports have 0 total"""

        # initialize data
        self.create_final_reports(count=10, total=0.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # Validate average
        self.assertEqual(calcs.get_average_num(), 0)

    def test_get_average_score_50(self):
        """Validate average number when all reports have 50 total"""

        # initialize data
        self.create_final_reports(count=10, total=50.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average
        self.assertEqual(calcs.get_average_num(), 50.0)

    def test_get_average_score_100(self):
        """Validate average number when all reports have 100 total"""

        # initialize data
        self.create_final_reports(count=10, total=100.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average
        self.assertEqual(calcs.get_average_num(), 100.0)

    def test_get_average_employees_0(self):
        """Validate average number when there are no reports"""

        # initialize data
        self.create_final_reports(count=0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average
        self.assertEqual(calcs.get_average_num(), 0.0)

    def test_get_average_range_0(self):
        """Validate average range when all reports have 0 total (low range)"""

        # initialize data
        self.create_final_reports(count=10, total=0.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "low")

    def test_get_average_range_59(self):
        """Validate average range when all reports have 59 total (low range)"""

        # initialize data
        self.create_final_reports(count=10, total=59.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "low")

    def test_get_average_range_60(self):
        """Validate average range when all reports have 60 total (medium range)"""

        # initialize data
        self.create_final_reports(count=10, total=60.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "medium")

    def test_get_average_range_79(self):
        """Validate average range when all reports have 79 total (medium range)"""

        # initialize data
        self.create_final_reports(count=10, total=79.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "medium")

    def test_get_average_range_80(self):
        """Validate average range when all reports have 80 total (high range)"""

        # initialize data
        self.create_final_reports(count=10, total=80.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "high")

    def test_get_average_range_100(self):
        """Validate average range when all reports have 100 total (high range)"""

        # initialize data
        self.create_final_reports(count=10, total=100.0)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "high")

    def test_get_average_question_groups_ordered_random_options(self):
        """Validate average areas ordered by average (max to min)"""

        # initialize data
        self.create_final_reports(count=10, total_random=True)
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())
        data = calcs.get_average_question_groups_ordered()

        # Validate if options are in correct order
        data_values = list(data.values())
        data_values_max_to_min = sorted(data_values, reverse=True)
        self.assertEqual(data_values, data_values_max_to_min)

    def test_get_average_question_groups_ordered_specific_order(self):
        """Validate average areas ordered by specific order:

        Set specific question groups to be first and last in data,
        then validate that they are in the correct order
        """

        # initialize data
        self.create_final_reports(count=10, total_random=True)

        # Update 2 random questions gropup score, in each employee
        qg_lower = survey_models.QuestionGroup.objects.order_by("?").first()
        qg_upper = survey_models.QuestionGroup.objects.order_by("?").first()
        if qg_lower == qg_upper:
            self.test_get_average_question_groups_ordered_random_options()
            return

        qg_lower_all_results = survey_models.ReportQuestionGroupTotal.objects.filter(
            question_group=qg_lower,
        )
        qg_lower_all_results.update(total=0)
        qg_upper_all_results = survey_models.ReportQuestionGroupTotal.objects.filter(
            question_group=qg_upper,
        )
        qg_upper_all_results.update(total=100)

        # Do calcs
        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())
        data = calcs.get_average_question_groups_ordered()

        # Validate if options are in correct order
        data_values = list(data.values())
        data_values_max_to_min = sorted(data_values, reverse=True)
        self.assertEqual(data_values, data_values_max_to_min)
        self.assertEqual(data[qg_lower.name], 0)
        self.assertEqual(data[qg_upper.name], 100)
        self.assertNotEqual(qg_lower.name, list(data.keys())[0])
        self.assertNotEqual(qg_upper.name, list(data.keys())[-1])
