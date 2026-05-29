import math
import random

from core.tests_base.test_models import TestSurveyModelBase
from django.core.management import call_command
from survey import models as survey_models
from utils.survey_calcs_group import SurveyCalcsGroup, SurveyCalcsGroupTexts
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

    def get_lower_outlier_value(self, target_std_dev, missing_count=1):
        """
        Calculates the lower value needed for a set of missing identical numbers
        alongside a set of values equal to 100 to achieve a specific target
        standard deviation in Django. Total dataset size is always 100.

        Args:
            target_std_dev (float): The standard deviation value to achieve
            missing_count (int): How many identical missing items you need to fill (e.g., 1, 10)
            sample (bool): Set to True if you use Django's StdDev(sample=True)

        Returns:
            float: The exact value needed for the missing items
        """
        TOTAL_ITEMS = 100
        identical_count = TOTAL_ITEMS - missing_count

        # Population StdDev formula adjustment for multiple identical outliers
        factor = TOTAL_ITEMS / math.sqrt(identical_count * missing_count)
        return 100.0 - (target_std_dev * factor)

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

            if not total_random:
                report.total = total
                report.save()

            reports.append(report)

        return reports

    def test_get_employees_number(self):
        """Validate correct count of reports"""

        # initialize data
        self.create_final_reports(count=10)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        # Valdiate num
        self.assertEqual(calcs.get_employees_number(), 10)

    def test_get_average_score_0(self):
        """Validate average number when all reports have 0 total"""

        # initialize data
        self.create_final_reports(count=10, total=0.0)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        # Validate average
        self.assertEqual(calcs.get_average(), 0)

    def test_get_average_score_50(self):
        """Validate average number when all reports have 50 total"""

        # initialize data
        self.create_final_reports(count=10, total=50.0)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        # validate average
        self.assertEqual(calcs.get_average(), 50.0)

    def test_get_average_score_100(self):
        """Validate average number when all reports have 100 total"""

        # initialize data
        self.create_final_reports(count=10, total=100.0)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        # validate average
        self.assertEqual(calcs.get_average(), 100.0)

    def test_get_average_employees_0(self):
        """Validate average number when there are no reports"""

        # initialize data
        self.create_final_reports(count=0)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        # validate average
        self.assertEqual(calcs.get_average(), 0.0)

    def test_get_average_range_0(self):
        """Validate average range when all reports have 0 total (low range)"""

        # initialize data
        self.create_final_reports(count=10, total=0.0)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "low")

    def test_get_average_range_59(self):
        """Validate average range when all reports have 59 total (low range)"""

        # initialize data
        self.create_final_reports(count=10, total=59.0)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "low")

    def test_get_average_range_60(self):
        """Validate average range when all reports have 60 total (medium range)"""

        # initialize data
        self.create_final_reports(count=10, total=60.0)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "medium")

    def test_get_average_range_79(self):
        """Validate average range when all reports have 79 total (medium range)"""

        # initialize data
        self.create_final_reports(count=10, total=79.0)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "medium")

    def test_get_average_range_80(self):
        """Validate average range when all reports have 80 total (high range)"""

        # initialize data
        self.create_final_reports(count=10, total=80.0)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "high")

    def test_get_average_range_100(self):
        """Validate average range when all reports have 100 total (high range)"""

        # initialize data
        self.create_final_reports(count=10, total=100.0)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        # validate average range
        self.assertEqual(calcs.get_average_range(), "high")

    def test_get_general_summary(self):
        """Validate the returned text for each general summary range"""
        from unittest.mock import patch
        
        with patch.object(SurveyCalcsGroupTexts, "get_average_range", return_value="low"):
            calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.none())
            self.assertIn("base tecnológica limitada", calcs.get_general_summary())

        with patch.object(SurveyCalcsGroupTexts, "get_average_range", return_value="medium"):
            calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.none())
            self.assertIn("base tecnológica funcional", calcs.get_general_summary())

        with patch.object(SurveyCalcsGroupTexts, "get_average_range", return_value="high"):
            calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.none())
            self.assertIn("base tecnológica sólida", calcs.get_general_summary())

    def test_get_dispersion_summary(self):
        """Validate the returned text for each dispersion summary range"""
        from unittest.mock import patch
        
        with patch.object(SurveyCalcsGroupTexts, "get_standard_deviation_total_range", return_value="low"):
            calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.none())
            self.assertIn("nivel relativamente homogéneo", calcs.get_dispersion_summary())

        with patch.object(SurveyCalcsGroupTexts, "get_standard_deviation_total_range", return_value="medium"):
            calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.none())
            self.assertIn("diferencias moderadas entre participantes", calcs.get_dispersion_summary())

        with patch.object(SurveyCalcsGroupTexts, "get_standard_deviation_total_range", return_value="high"):
            calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.none())
            self.assertIn("diferencias importantes entre participantes", calcs.get_dispersion_summary())

    def test_get_strength_areas(self):
        """Validate the returned list for strength areas based on top 2 areas"""
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        from unittest.mock import patch
        
        # Mock get_average_areas_ordered to return specific areas
        mock_ordered_areas = [
            {"area": "CD", "average": 90.0},
            {"area": "CS", "average": 85.0},
            {"area": "TN", "average": 70.0}
        ]
        
        with patch.object(calcs, "get_average_areas_ordered", return_value=mock_ordered_areas):
            summary = calcs.get_strength_areas()
            self.assertEqual(summary, ["Cultura digital", "Ciberseguridad"])

    def test_get_weakness_areas(self):
        """Validate the returned list for weakness areas based on bottom 2 areas"""
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        from unittest.mock import patch
        
        # Mock get_average_areas_ordered to return specific areas
        mock_ordered_areas = [
            {"area": "CD", "average": 90.0},
            {"area": "TN", "average": 70.0},
            {"area": "CS", "average": 65.0}
        ]
        
        with patch.object(calcs, "get_average_areas_ordered", return_value=mock_ordered_areas):
            summary = calcs.get_weakness_areas()
            # lowest is at -1, second lowest at -2
            self.assertEqual(summary, ["Ciberseguridad", "Tecnología y negocios"])

    def test_get_priority_summary(self):
        """Validate the returned text for priority summary based on weakness pairs"""
        from unittest.mock import patch
        
        with patch.object(SurveyCalcsGroupTexts, "get_weakness_areas", return_value=["Cultura digital", "Ciberseguridad"]):
            calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.none())
            self.assertIn("Resulta prioritario fortalecer la cultura digital incorporando prácticas básicas de seguridad tecnológica", calcs.get_priority_summary())

        with patch.object(SurveyCalcsGroupTexts, "get_weakness_areas", return_value=["Tecnología y negocios", "Futuro sustentable e inclusivo"]):
            calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.none())
            self.assertIn("Resulta prioritario fortalecer la comprensión de cómo la tecnología influye en el modelo de negocio", calcs.get_priority_summary())

        with patch.object(SurveyCalcsGroupTexts, "get_weakness_areas", return_value=["Cultura digital"]):
            calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.none())
            self.assertIn("No se han identificado suficientes áreas de oportunidad", calcs.get_priority_summary())

    def test_get_max_min_scores(self):
        """Validate get_max_score and get_min_score return correct values"""
        self.create_final_reports(count=5)
        # Set specific total scores
        reports = list(survey_models.Report.objects.all())
        reports[0].total = 85.50
        reports[0].save()
        reports[1].total = 42.25
        reports[1].save()
        reports[2].total = 95.75
        reports[2].save()
        reports[3].total = 60.00
        reports[3].save()
        reports[4].total = 55.50
        reports[4].save()

        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())
        self.assertEqual(calcs.get_max_score(), 95.75)
        self.assertEqual(calcs.get_min_score(), 42.25)

    def test_get_participant_distribution(self):
        """Validate get_participant_distribution returns correct counts and percentages"""
        self.create_final_reports(count=5)
        reports = list(survey_models.Report.objects.all())
        # Set specific total scores:
        # Advanced (total >= 80): 2
        # Intermediate (total >= 60 and < 80): 2
        # Basic (total < 60): 1
        reports[0].total = 85.0
        reports[0].save()
        reports[1].total = 80.0
        reports[1].save()
        reports[2].total = 79.9
        reports[2].save()
        reports[3].total = 60.0
        reports[3].save()
        reports[4].total = 59.9
        reports[4].save()

        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())
        distribution = calcs.get_participant_distribution()

        # We expect a list of three objects:
        # high: count=2, percentage=40%
        # medium: count=2, percentage=40%
        # low: count=1, percentage=20%
        expected = [
            {"level": "high", "count": 2, "percentage": 40.0},
            {"level": "medium", "count": 2, "percentage": 40.0},
            {"level": "low", "count": 1, "percentage": 20.0},
        ]
        self.assertEqual(distribution, expected)

    def test_get_average_question_groups_ordered_random_options(self):
        """Validate average areas ordered by average (max to min)"""

        # initialize data
        self.create_final_reports(count=10, total_random=True)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())
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
            self.test_get_average_question_groups_ordered_specific_order()
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
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())
        data = calcs.get_average_question_groups_ordered()

        # Validate if options are in correct order
        data_values = list(data.values())
        data_values_max_to_min = sorted(data_values, reverse=True)
        self.assertEqual(data_values, data_values_max_to_min)
        self.assertEqual(data[qg_lower.name], 0)
        self.assertEqual(data[qg_upper.name], 100)
        self.assertNotEqual(qg_lower.name, list(data.keys())[0])
        self.assertNotEqual(qg_upper.name, list(data.keys())[-1])

    def test_get_standard_deviation_total_50(self):
        """Validate standard deviation total when all reports have same total (50)"""

        # initialize data
        self.create_final_reports(count=10, total=50.0)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        # Validate standard deviation
        self.assertEqual(calcs.get_standard_deviation_total(), 0.0)

    def test_get_standard_deviation_total_random(self):
        """Validate standard deviation total when all reports have random total"""

        # initialize data
        self.create_final_reports(count=10, total_random=True)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        # Validate standard deviation
        self.assertNotEqual(calcs.get_standard_deviation_total(), 0.0)

    def test_get_standard_deviation_total_99_100__1_90(self):
        """Validate standard deviation total when all reports have 100 and one has 90 total"""

        # initialize data
        self.create_final_reports(count=99, total=100.0)
        self.create_final_reports(count=1, total=90.0)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        # Validate standard deviation
        self.assertLess(calcs.get_standard_deviation_total(), 1.0)

    def test_get_standard_deviation_total_9_100__1_90(self):
        """Validate standard deviation total when all reports have 100 and one has 90 total"""

        # initialize data
        self.create_final_reports(count=9, total=100.0)
        self.create_final_reports(count=1, total=90.0)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())

        # Validate standard deviation
        self.assertEqual(calcs.get_standard_deviation_total(), 3.0)

    def test_get_standard_deviation_total_range(self):
        """Validate standard deviation total range for all required values"""
        values = {
            0.0: "low",
            7.9: "low",
            8.0: "low",
            8.1: "medium",
            14.9: "medium",
            15.0: "medium",
            15.1: "high",
        }

        for value, expected_range in values.items():
            with self.subTest(value=value):
                survey_models.Report.objects.all().delete()
                self.create_final_reports(count=90, total=100)
                required_value = self.get_lower_outlier_value(
                    target_std_dev=value, missing_count=10
                )
                self.create_final_reports(count=10, total=required_value)
                calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())
                self.assertAlmostEqual(
                    calcs.get_standard_deviation_total(), value, places=1
                )
                self.assertEqual(
                    calcs.get_standard_deviation_total_range(), expected_range
                )

    def test_get_average_areas_ordered_random_options(self):
        """Validate average areas ordered by average (max to min)"""

        # initialize data
        self.create_final_reports(count=10, total_random=True)
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())
        data = calcs.get_average_areas_ordered()

        # Validate if areas are in correct order
        data_values = [item["average"] for item in data]
        data_values_max_to_min = sorted(data_values, reverse=True)
        self.assertEqual(data_values, data_values_max_to_min)

    def test_get_average_areas_ordered_specific_order(self):
        """Validate average areas ordered by specific order:

        Set specific question groups to be first and last in data,
        then validate that they are in the correct order
        """

        # initialize data
        self.create_final_reports(count=10, total_random=True)

        # Update 2 random areas score, in each employee
        area_lower = survey_models.TextPDFSummary.objects.order_by("?").first()
        area_upper = survey_models.TextPDFSummary.objects.order_by("?").first()
        if area_lower.paragraph_type == area_upper.paragraph_type:
            self.test_get_average_areas_ordered_specific_order()
            return

        area_lower_all_results = survey_models.ReportSummaryScore.objects.filter(
            paragraph_type=area_lower.paragraph_type,
        )
        area_lower_all_results.update(score=0)
        area_upper_all_results = survey_models.ReportSummaryScore.objects.filter(
            paragraph_type=area_upper.paragraph_type,
        )
        area_upper_all_results.update(score=100)

        # Do calcs
        calcs = SurveyCalcsGroupTexts(survey_models.Report.objects.all())
        data = calcs.get_average_areas_ordered(use_summary=True)

        # Validate if options are in correct order
        data_values = [item["average"] for item in data]
        data_values_max_to_min = sorted(data_values, reverse=True)
        self.assertEqual(data_values, data_values_max_to_min)
        
        lower_item = next((item for item in data if item["area"] == area_lower.paragraph_type), None)
        upper_item = next((item for item in data if item["area"] == area_upper.paragraph_type), None)
        
        self.assertIsNotNone(lower_item)
        self.assertIsNotNone(upper_item)
        self.assertEqual(lower_item["average"], 0)
        self.assertEqual(upper_item["average"], 100)
        self.assertNotEqual(area_lower.paragraph_type, data[0]["area"])
        self.assertNotEqual(area_upper.paragraph_type, data[-1]["area"])

    def test_get_strategic_profiles(self):
        """Validate get_strategic_profiles correctly classifies participants"""
        # Clear existing reports to make the test hermetic
        survey_models.Report.objects.all().delete()
        survey_models.Participant.objects.all().delete()

        options = self.get_selected_options(score=0)

        # p1: High Score (90), Position director -> High Influence => Ambassador
        p1_report = self.create_report(options=options)
        p1_report.participant.position = "director"
        p1_report.participant.name = "Monica Rodriguez"
        p1_report.participant.save()
        p1_report.total = 90.0
        p1_report.save()

        # p2: High Score (85), Position analista -> Low Influence => Champion
        p2_report = self.create_report(options=options)
        p2_report.participant.position = "analista"
        p2_report.participant.name = "John Doe"
        p2_report.participant.save()
        p2_report.total = 85.0
        p2_report.save()

        # p3: Low Score (45), Position director -> High Influence => Risk
        p3_report = self.create_report(options=options)
        p3_report.participant.position = "director"
        p3_report.participant.name = "Carlos Rodriguez"
        p3_report.participant.save()
        p3_report.total = 45.0
        p3_report.save()

        # p4: Medium Score (70), Position director -> High Influence => Excluded (None)
        p4_report = self.create_report(options=options)
        p4_report.participant.position = "director"
        p4_report.participant.name = "Sarah Smith"
        p4_report.participant.save()
        p4_report.total = 70.0
        p4_report.save()

        # p5: Low Score (50), Position analista -> Low Influence => Excluded (None)
        p5_report = self.create_report(options=options)
        p5_report.participant.position = "analista"
        p5_report.participant.name = "David Miller"
        p5_report.participant.save()
        p5_report.total = 50.0
        p5_report.save()

        calcs = SurveyCalcsGroup(survey_models.Report.objects.all())
        profiles = calcs.get_strategic_profiles()

        self.assertEqual(profiles["ambassadors"], ["Monica Rodriguez"])
        self.assertEqual(profiles["champions"], ["John Doe"])
        self.assertEqual(profiles["risks"], ["Carlos Rodriguez"])
        # Medium tech participants and low-influence low-tech are excluded
        all_names = (
            profiles["ambassadors"] + profiles["champions"] + profiles["risks"]
        )
        self.assertNotIn("Sarah Smith", all_names)
        self.assertNotIn("David Miller", all_names)

