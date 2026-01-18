import math

from django.http import HttpResponse
from django.core.management import call_command
from django.contrib import messages

from bs4 import BeautifulSoup

from core.tests_base.test_admin import TestAdminBase
from core.tests_base.test_models import TestSurveyModelBase
from survey import models as survey_models
from utils.media import get_media_url


class CompanyAdminTestCase(TestAdminBase):
    """Testing company admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/company/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class SurveyAdminTestCase(TestAdminBase):
    """Testing survey admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/survey/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class QuestionGroupAdminTestCase(TestAdminBase):
    """Testing question group admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/questiongroup/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class QuestionAdminTestCase(TestAdminBase):
    """Testing question admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/question/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class QuestionOptionAdminTestCase(TestAdminBase, TestSurveyModelBase):
    """Testing question option admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/questionoption/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)

    def test_custom_filter_survey_filter(self):
        """Validate survey filter working"""

        # Create required data
        survey_1 = self.create_survey()
        survey_2 = self.create_survey()
        question_group_1 = self.create_question_group(survey=survey_1)
        question_1 = self.create_question(question_group=question_group_1)
        self.create_question_option(question=question_1)

        # Validate survey filter
        self.validate_custom_filter("survey", survey_1.id, survey_2.id)

    def test_custom_filter_question_group_filter(self):
        """Validate question group filter working"""

        # Create required data
        question_group_1 = self.create_question_group()
        question_group_2 = self.create_question_group()
        question_1 = self.create_question(question_group=question_group_1)
        self.create_question_option(question=question_1)

        # Validate question group filter
        self.validate_custom_filter(
            "question_group", question_group_1.id, question_group_2.id
        )


class ParticipantAdminTestCase(TestAdminBase):
    """Testing participant admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/participant/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class AnswerAdminTestCase(TestAdminBase, TestSurveyModelBase):
    """Testing answer admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/answer/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)

    def test_custom_filter_survey_filter(self):
        """Validate survey filter working"""

        # Create required data
        survey_1 = self.create_survey()
        survey_2 = self.create_survey()
        question_group_1 = self.create_question_group(survey=survey_1)
        question_1 = self.create_question(question_group=question_group_1)
        option = self.create_question_option(question=question_1)
        self.create_answer(question_option=option)

        # Validate survey filter
        self.validate_custom_filter("survey", survey_1.id, survey_2.id)

    def test_custom_filter_question_group_filter(self):
        """Validate question group filter working"""

        # Create required data
        question_group_1 = self.create_question_group()
        question_group_2 = self.create_question_group()
        question_1 = self.create_question(question_group=question_group_1)
        option = self.create_question_option(question=question_1)
        self.create_answer(question_option=option)

        # Validate question group filter
        self.validate_custom_filter(
            "question_group", question_group_1.id, question_group_2.id
        )

    def test_custom_filter_question_filter(self):
        """Validate question filter working"""

        # Create required data
        question_1 = self.create_question()
        question_2 = self.create_question()
        option = self.create_question_option(question=question_1)
        self.create_answer(question_option=option)

        # Validate question filter
        self.validate_custom_filter("question", question_1.id, question_2.id)


class ReportAdminTestCase(TestAdminBase, TestSurveyModelBase):
    """Testing report admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/report/"

        # Delete other reports
        survey_models.Report.objects.all().delete()

        # Create required data
        self.survey = self.create_survey()
        self.participant = self.create_participant()
        self.company = self.create_company()

        # Load fixtures
        call_command("apps_loaddata")
        call_command("initial_loaddata")

        # Create report
        self.create_report()
        self.report = survey_models.Report.objects.all().last()

        # Set question gorup scores to same percentage
        question_groups = survey_models.QuestionGroup.objects.all()
        for question_group in question_groups:
            question_group.survey_percentage = 100 / len(question_groups)
            question_group.save()

        # Create 10 questions in each question group
        questions = []
        options = []
        for question_group in question_groups:
            for _ in range(10):
                question = self.create_question(question_group=question_group)
                questions.append(question)
                options.append(
                    self.create_question_option(question=question, text="yes", points=1)
                )

        # Calculate correct answers
        score = 90
        correct_answers = math.floor(len(options) * score / 100)

        # Set required correct answers
        for question_index in range(correct_answers):
            self.create_answer(
                participant=self.participant, question_option=options[question_index]
            )

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)

    def __validate_disabled_see_report_btn(self, response: HttpResponse):
        """Validate disabled see report button

        Args:
            response (HttpResponse): Response of the request
        """

        # Validate http status
        self.assertEqual(response.status_code, 200)

        # Validate link "Ver Reporte" disabled
        soup = BeautifulSoup(response.content, "html.parser")
        link = soup.select_one(".field-custom_links > a")
        self.assertIsNotNone(link)
        self.assertIn("disabled", link["class"])
        self.assertIn("btn-secondary", link["class"])
        self.assertIsNone(link.get("href"))
        self.assertEqual(link.get("disabled"), "")

    def test_custom_links_see_report_pending(self):
        """Validate custom link "Ver Reporte" working for pending report"""

        # Update report status
        self.report.status = "pending"
        self.report.save()

        # Validate response
        response = self.client.get(f"{self.endpoint}")

        self.__validate_disabled_see_report_btn(response)

    def test_custom_links_see_report_processing(self):
        """Validate custom link "Ver Reporte" working for processing report"""

        # Update report status
        self.report.status = "processing"
        self.report.save()

        # Validate response
        response = self.client.get(f"{self.endpoint}")

        self.__validate_disabled_see_report_btn(response)

    def test_custom_links_see_report_error(self):
        """Validate custom link "Ver Reporte" working for error report"""

        # Update report status
        self.report.status = "error"
        self.report.save()

        # Validate response
        response = self.client.get(f"{self.endpoint}")

        self.__validate_disabled_see_report_btn(response)

    def test_custom_links_see_report_completed(self):
        """Validate custom link "Ver Reporte" working for completed report"""

        # create real report with command
        call_command("generate_next_report")

        response = self.client.get(f"{self.endpoint}")

        self.report.refresh_from_db()
        pdf_url = get_media_url(self.report.pdf_file)

        # Validate response
        self.assertEqual(response.status_code, 200)

        # Validate link "Ver Reporte" disabled
        soup = BeautifulSoup(response.content, "html.parser")
        link = soup.select_one(".field-custom_links > a")
        self.assertIsNotNone(link)
        self.assertNotIn("disabled", link["class"])
        self.assertIn("btn-primary", link["class"])
        self.assertEqual(link.get("href"), pdf_url)
        self.assertIsNone(link.get("disabled"))

    def test_action_set_to_pending(self):
        """Validate action set to pending working"""

        # Update report status
        self.report.status = "completed"
        self.report.save()

        # Simulate action
        self.client.post(
            f"{self.endpoint}",
            {"action": "set_to_pending", "_selected_action": [self.report.id]},
        )

        self.report.refresh_from_db()
        self.assertEqual(self.report.status, "pending")

    def test_action_create_reports_download(self):
        """Validate action create reports download working"""

        # Simulate action
        response = self.client.post(
            f"{self.endpoint}",
            {"action": "create_reports_download", "_selected_action": [self.report.id]},
            follow=True,
        )

        # Validate download created in table
        self.assertEqual(survey_models.ReportsDownload.objects.count(), 1)

        # Validate message
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Descarga creada correctamente. Consulta tabla de descargas para ver el estado.",
        )


class ReportQuestionGroupTotalAdminTestCase(TestAdminBase, TestSurveyModelBase):
    """Testing report question group total admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/reportquestiongrouptotal/"

    def test_search_bar(self):
        """Validate search bar working"""
        self.submit_search_bar(self.endpoint)


class TextPDFQuestionGroupAdminTestCase(TestAdminBase, TestSurveyModelBase):
    """Testing text pdf question group admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/textpdfquestiongroup/"

    def test_search_bar(self):
        """Validate search bar working"""
        self.submit_search_bar(self.endpoint)


class TextPDFSummaryAdminTestCase(TestAdminBase, TestSurveyModelBase):
    """Testing text pdf summary admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/textpdfsummary/"

    def test_search_bar(self):
        """Validate search bar working"""
        self.submit_search_bar(self.endpoint)


class CompanyDesiredScoreAdminTestCase(TestAdminBase, TestSurveyModelBase):
    """Testing company desired score admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/companydesiredscore/"

    def test_search_bar(self):
        """Validate search bar working"""
        self.submit_search_bar(self.endpoint)


class ReportsDownloadAdminTestCase(TestAdminBase, TestSurveyModelBase):
    """Testing reports download admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/reportsdownload/"
        self.company = self.create_company()
        self.survey = self.create_survey()

    def test_search_bar(self):
        """Validate search bar working"""
        self.submit_search_bar(self.endpoint)

    def test_reports_num_column(self):
        """Validate reports_num calculated field in list display"""

        # Create reports
        report_1 = self.create_report()
        report_2 = self.create_report()

        # Create ReportsDownload
        reports_download = survey_models.ReportsDownload.objects.create(
            status="pending"
        )
        reports_download.reports.set([report_1, report_2])

        # Get admin page
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 200)

        # Validate column value
        soup = BeautifulSoup(response.content, "html.parser")
        reports_num_cell = soup.select_one(".field-reports_num")
        self.assertIsNotNone(reports_num_cell)
        self.assertEqual(reports_num_cell.get_text(strip=True), "2")
