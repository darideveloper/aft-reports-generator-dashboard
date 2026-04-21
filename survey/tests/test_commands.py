import os
import re
import json
import random
import shutil
from time import sleep

from django.core.management import call_command
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase
from rest_framework import status

from core.tests_base.test_models import TestSurveyModelBase
from survey import models as survey_models
from utils.media import get_media_url
from utils.survey_calcs import SurveyCalcs

import requests
from PyPDF2 import PdfReader
from playwright.sync_api import sync_playwright

from unittest.mock import MagicMock, patch


class GenerateNextReportBase(TestSurveyModelBase, APITestCase):
    """
    Base class with shared method and initial env variables to
    test generate_next_report command
    """

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Load data
        call_command("apps_loaddata")
        call_command("initial_loaddata")

        # Create report
        self.company = self.create_company()
        self.participant = self.create_participant(company=self.company)
        self.survey = survey_models.Survey.objects.get(id=1)

        # Login to client with session
        username = "test_user"
        password = "test_pass"
        User.objects.create_superuser(
            username=username,
            email="test@gmail.com",
            password=password,
        )
        self.client.login(username=username, password=password)

        self.questions, self.options = self.__create_question_and_options()
        self.question_groups = survey_models.QuestionGroup.objects.all()

    def __create_question_and_options(self) -> tuple:
        """
        Create questions and options in each question group

        Returns:
            tuple: questions and options
        """

        # Set question gorup scores to same percentage
        question_groups = survey_models.QuestionGroup.objects.all()
        for question_group in question_groups:
            question_group.survey_percentage = 100 / len(question_groups)
            question_group.save()

        # Create 10 questions in each question group
        for question_group in question_groups:
            for _ in range(10):
                question = self.create_question(question_group=question_group)
                self.create_question_option(question=question, text="yes", points=1)

        questions = survey_models.Question.objects.all()
        options = survey_models.QuestionOption.objects.all()

        return questions, options

    def get_selected_options(self, score: int) -> list[int]:
        """
        Get selected options in each question group based on score

        Args:
            score: Score to get selected options

        Returns:
            list[int]: Selected options ids
        """
        selected_options_ids = []
        for question_group in self.question_groups:
            selected_options = self.options.filter(
                points=1, question__question_group=question_group
            )
            selected_options_num = int(score * len(selected_options) / 100)
            selected_options = selected_options[:selected_options_num]
            for option in selected_options:
                selected_options_ids.append(option.id)
        return selected_options_ids

    def create_get_pdf(self):
        """
        Create pdf report with generate_next_report command and return local path

        Returns:
            os.path: Local path of the new pdf file
        """

        # Detect files already in pdf folder
        pdf_folder = os.path.join(settings.BASE_DIR, "media", "reports")
        pdf_files = os.listdir(pdf_folder)
        old_pdf_files = [file for file in pdf_files if file.endswith(".pdf")]

        # Generate next pdf
        call_command("generate_next_report")

        # detect new report
        pdf_files = os.listdir(pdf_folder)
        new_pdf_files = [file for file in pdf_files if file.endswith(".pdf")]
        new_files = [file for file in new_pdf_files if file not in old_pdf_files]
        self.assertEqual(len(new_files), 1)
        new_file = new_files[0]
        pdf_path = os.path.join(pdf_folder, new_file)

        return pdf_path

    def create_report_question_group_totals_data(self):
        """
        Create report question group totals data

        Returns:
            survey: Survey object (if not provided, a new survey will be created)
            options: List of QuestionOption objects
            question_groups: List of QuestionGroup objects
        """

        # Generate initial data

        # Get question groups from survey
        question_groups = survey_models.QuestionGroup.objects.filter(
            survey=self.survey
        ).order_by("survey_index")

        # Create 10 questions in each question group
        for question_group in question_groups:
            for _ in range(10):
                self.create_question(question_group=question_group)

        questions = survey_models.Question.objects.all()

        # Create 2 options in each question (yes and no)
        for question in questions:
            for option in ["yes", "no"]:
                self.create_question_option(
                    question=question,
                    text=option,
                    points=1 if option == "yes" else 0,
                )

        options = survey_models.QuestionOption.objects.all()

        return self.survey, options, question_groups

    def validate_text_in_pdf(self, pdf_path: str, text: str):
        """
        Validate text is in pdf

        Args:
            pdf_path: Path to the pdf file
            text: Text to validate
            page: Page to validate

        Returns:
            bool: True if text is in pdf
        """
        # Read pdf text content
        pdf_text = ""
        with open(pdf_path, "rb") as f:
            pdf_reader = PdfReader(f)
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()

        # Validate text in pdf
        # Normalize both texts:
        def normalize(s):
            s = s.lower()  # To lowercase
            s = re.sub(r"\s+", " ", s)  # Replace multiple spaces/line breaks with one
            s = s.strip()  # Remove leading/trailing spaces
            return s

        normalized_text = normalize(text)
        normalized_page = normalize(pdf_text)

        # Check if text is in pdf
        return normalized_text in normalized_page


class GenerateNextReportCreationTestCase(GenerateNextReportBase):
    """
    Test pdf report created with generate_next_report command
    """

    def validate_report(self, report: survey_models.Report):
        """
        Validate report data

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

    def test_many_pending_reports(self):
        """
        Test with many pending reports
        Expect:
            - The command should update the status of the report to completed
        """

        # delete initial reports
        survey_models.Report.objects.all().delete()

        # Create 3 reports
        reports = []
        for _ in range(3):
            reports.append(self.create_report())

        call_command("generate_next_report")

        # Validate report data
        self.validate_report(reports[0])

        # Validate other reports are still pending
        for other_report in reports[1:]:
            other_report.refresh_from_db()
            self.assertEqual(other_report.status, "pending")

    def test_single_report(self):
        """
        Test with a single report
        Expect:
            - The command should update the status of the report to completed
        """

        # Create report
        self.report = self.create_report()

        call_command("generate_next_report")

        # Validate report data
        self.validate_report(self.report)

    def test_no_pending_reports(self):
        """
        Test with no pending reports
        Expect:
            - The command should do nothing (skip all reports)
        """

        # Create 3 reports in completed status
        for _ in range(3):
            report = self.create_report()
            report.status = "completed"
            report.save()

        call_command("generate_next_report")

        # Validate no reports are ready to be processed or completed
        self.assertEqual(
            survey_models.Report.objects.filter(status="pending").count(), 0
        )
        self.assertEqual(
            survey_models.Report.objects.filter(status="completed").count(), 3
        )
        self.assertEqual(survey_models.Report.objects.filter(status="error").count(), 0)

    def test_percentages_2_decimal_places(self):
        """
        Test percentages are 2 decimal places
        """
        self.company.use_average = False
        self.company.save()

        options_100 = self.get_selected_options(score=100)
        self.create_report(options=options_100)
        pdf_path = self.create_get_pdf()
        self.validate_text_in_pdf(pdf_path, "100.00%")

        options_0 = self.get_selected_options(score=0)
        self.create_report(options=options_0)
        pdf_path = self.create_get_pdf()
        self.validate_text_in_pdf(pdf_path, "0.00%")


class GenerateNextReportBellChartTestCase(GenerateNextReportBase):
    """
    Test pdf report data is generated correctly (bell chart)
    """

    def test_manual_check(self):
        """
        Validate bell chart data is generated correctly (manually user check required)
        """
        company_1 = self.create_company()
        company_2 = self.create_company()

        # Create reports with scores from 40 to 90, in each company
        companies = [company_1, company_2]
        for company in companies:
            company_index = companies.index(company)
            min_score = 40 + company_index * 10
            max_score = 90 + company_index * 10
            for score in range(min_score, max_score):

                # Create report with score
                selected_options = self.get_selected_options(score=score)
                self.create_report(
                    options=selected_options, invitation_code=company.invitation_code
                )

        # create and get pdf
        self.create_report(invitation_code=company_1.invitation_code)
        pdf_path = self.create_get_pdf()

        # Request to the user to validate
        print(">>> New file url: " + pdf_path + "\nManual check of bell chart required")
        sleep(60)


class GenerateNextReportCheckBoxesTestCase(GenerateNextReportBase):
    """
    Test pdf report data is generated correctly (check boxes)
    """

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Delete initial reports
        survey_models.Report.objects.all().delete()

        # Create 100 reports
        for score in range(0, 100):
            self.create_report()
            report = survey_models.Report.objects.all().last()
            report.total = score
            report.status = "completed"
            report.save()

    def __get_pdf_squares(self, pdf_path: str):
        """
        Get squares from pdf

        Args:
            pdf_path: Path to the pdf file

        Returns:
            list: List of squares (reversed)
                Example: ["■", "□", "□", "□", "□", "□"]
        """
        # Read pdf text content
        with open(pdf_path, "rb") as f:
            pdf_reader = PdfReader(f)
            page_3_text = pdf_reader.pages[2].extract_text()
        page_3_lines = page_3_text.split("\n")

        # get range squaresç
        range_squares = page_3_lines[16:22]

        return range_squares

    def __test_square_position(self, score: int, position: int):
        """
        Base test to validate square position (correct greade code)

        Args:
            score: Score to test
            position: Position of the square
        """

        # Create report with specific score
        selected_options = self.get_selected_options(score=score)
        self.create_report(options=selected_options)

        # create and get pdf
        pdf_path = self.create_get_pdf()

        # Get squares from pdf text
        squares = self.__get_pdf_squares(pdf_path)

        # Validate mdp aquare position
        self.assertEqual(squares[position], "■")

    def test_mdp_0(self):
        """Validate grade code mdp for score 0"""

        self.__test_square_position(score=0, position=0)

    def test_mdp_19(self):
        """Validate grade code mdp for score 19"""

        self.__test_square_position(score=19, position=0)

    def test_mdp_20(self):
        """Validate grade code mdp for score 20"""

        self.__test_square_position(score=20, position=0)

    def test_dp_40(self):
        """Validate grade code dp for score 40"""

        self.__test_square_position(score=40, position=1)

    def test_p_60(self):
        """Validate grade code p for score 60"""

        self.__test_square_position(score=60, position=2)

    def test_ap_80(self):
        """Validate grade code ap for score 80"""

        self.__test_square_position(score=80, position=3)

    def test_mep_100(self):
        """Validate grade code mep for score 100"""

        self.__test_square_position(score=100, position=4)


class GenerateNextReportBarChartTestCase(GenerateNextReportBase):
    """
    Test pdf report data is generated correctly (bar chart)
    """

    def setUp(self):

        # Run parent setUp
        super().setUp()

        # Create data
        self.company = self.create_company()

        # Create data for 2 participants
        for _ in range(2):
            # Create participant and report
            random_score_question_group = random.randint(0, 100)
            for question_group in self.question_groups:
                question_group_options = self.options.filter(
                    question__question_group=question_group
                )
                selected_options_num = int(
                    random_score_question_group * len(question_group_options) / 100
                )
                selected_options = question_group_options[:selected_options_num]
                selected_options_ids = [option.id for option in selected_options]
                self.create_report(
                    options=selected_options_ids,
                    invitation_code=self.company.invitation_code,
                )

        # Use the first participant created in this test
        participants = survey_models.Participant.objects.filter(company=self.company)
        self.participant = participants.first()
        self.report = survey_models.Report.objects.get(
            survey=self.survey, participant=self.participant
        )

    def __get_question_group_total_avg(self, question_group_id: int):
        """
        Get question group total average

        Args:
            question_group_id: Question group id

        Returns:
            float: Question group total average
        """
        # Get question group
        question_group = survey_models.QuestionGroup.objects.get(id=question_group_id)

        # Get totals of the question group
        question_group_totals_objs = (
            survey_models.ReportQuestionGroupTotal.objects.filter(
                question_group=question_group
            )
        )
        question_group_totals = [total.total for total in question_group_totals_objs]
        question_group_totals_avg = sum(question_group_totals) / len(
            question_group_totals
        )

        return question_group_totals_avg

    def __validate_chart_data(self, chart_data: list, use_average: bool):
        """
        Validate chart data structure

        Args:
            chart_data: Chart data
            use_average: Use average
        """

        self.assertEqual(len(chart_data), len(self.question_groups))
        for question_group_json in chart_data:

            # Get objects
            question_group = survey_models.QuestionGroup.objects.get(
                name__icontains=question_group_json["titulo"]
            )
            question_group_total = survey_models.ReportQuestionGroupTotal.objects.get(
                report=self.report, question_group=question_group
            )

            # Validate general data
            self.assertIn(question_group_json["titulo"], question_group.name)
            self.assertEqual(question_group_json["valor"], question_group_total.total)
            self.assertEqual(
                question_group_json["descripcion"], question_group.details_bar_chart
            )

            # Validate fixed data
            self.assertEqual(question_group_json["maximo"], 100)
            self.assertEqual(question_group_json["minimo"], 0)

            if use_average:

                question_groups_totals_avg = self.__get_question_group_total_avg(
                    question_group.id
                )
                self.assertEqual(
                    question_group_json["promedio"], question_groups_totals_avg
                )
            else:
                # Validate reference line as fixed
                company_desired_score = survey_models.CompanyDesiredScore.objects.get(
                    company=self.company, question_group=question_group
                )
                self.assertEqual(
                    question_group_json["promedio"], company_desired_score.desired_score
                )

    def test_get_bar_chart_data_use_average_true(self):
        """Test get request with valid data"""

        # Set company use average to true
        self.company.use_average = True
        self.company.save()

        # Get data from surv
        survey_calcs = SurveyCalcs(
            participant=self.report.participant,
            survey=self.report.survey,
            report=self.report,
        )
        chart_data = survey_calcs.get_bar_chart_data(use_average=True)

        # Validate chart data
        self.__validate_chart_data(chart_data, use_average=True)

    def test_get_bar_chart_data_use_average_false(self):
        """Test get request with valid data"""

        # Set company use average to false
        self.company.use_average = False
        self.company.save()

        # Get data from survey_calcs
        survey_calcs = SurveyCalcs(
            participant=self.report.participant,
            survey=self.report.survey,
            report=self.report,
        )
        chart_data = survey_calcs.get_bar_chart_data(use_average=False)

        # Validate chart data
        self.__validate_chart_data(chart_data, use_average=False)

    def test_chart_rendered(self):
        """
        Test chart rendered as html from external service
        """

        # Validate with avg and fixed goal rate
        use_averages = [True, False]

        for use_average in use_averages:
            self.company.use_average = use_average
            self.company.save()

            # Get json data to submit to external service, from endpoint
            survey_calcs = SurveyCalcs(
                participant=self.report.participant,
                survey=self.report.survey,
                report=self.report,
            )
            chart_data = survey_calcs.get_bar_chart_data(use_average=use_average)
            json_data = {
                "chart_data": chart_data,
                "use_average": True,
            }
            json_data_encoded = json.dumps(json_data)

            # Validate graph generation running
            error_service_down = (
                f"Graph generation not running in {settings.TEST_BAR_CHART_ENDPOINT}"
            )
            remote_endpoint = settings.TEST_BAR_CHART_ENDPOINT
            try:
                response = requests.get(remote_endpoint)
                response.raise_for_status()
                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                    error_service_down,
                )
            except Exception as e:
                self.fail(f"{error_service_down}: {e}")

            # Add param
            remote_endpoint += f"?data={json_data_encoded}"

            # Open page with playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(remote_endpoint)
                page.wait_for_timeout(2000)

                # Save screenshot of the page in "/temp.png"
                current_dir = os.path.dirname(os.path.abspath(__file__))
                temp_path = os.path.join(current_dir, "temp.png")
                page.screenshot(path=temp_path)

                # Test visible data in web page
                for question_group in chart_data:

                    # Check alreayd generated data
                    self.assertIn(question_group["titulo"], page.content())
                    self.assertIn(question_group["descripcion"], page.content())
                    self.assertIn(str(int(question_group["promedio"])), page.content())


class GenerateNextReportTextPDFQuestionGroupTestCase(GenerateNextReportBase):
    """
    Test PDF text generation
    """

    def setUp(self):
        """Set up test data"""

        # setup initial data from parent class
        super().setUp()

        # Create apo data
        self.invitation_code = "test"
        self.data = {
            "invitation_code": self.invitation_code,
            "survey_id": 1,
            "participant": {
                "email": "test@test.com",
                "name": "Test User",
                "gender": "m",
                "birth_range": "1946-1964",
                "position": "director",
            },
            "answers": [],
        }
        self.endpoint = "/api/response/"

        # Create company with invitation code
        self.company = self.create_company(invitation_code=self.invitation_code)

    def _test_pdf_text_generation(self, question_group_index: int, score: int):
        """
        Helper method to test PDF text generation for a question group and score.

        Args:
            question_group_index: Index of the question group (0-12)
            score: Score value to test (0, 49, 50, 51, 69, 70, 71, 99, 100)
        """
        # Determine expected min_score based on score
        # Determine expected min_score based on score
        # Since we have 10 questions, the score will be a multiple of 10
        effective_score = int(score / 10) * 10

        if effective_score <= 50:
            expected_min_score = 50
        elif effective_score <= 70:
            expected_min_score = 70
        else:
            expected_min_score = 100

        selected_options = self.get_selected_options(score=score)
        self.create_report(
            options=selected_options, invitation_code=self.invitation_code
        )

        # create and get pdf
        pdf_path = self.create_get_pdf()

        # Validate text in pdf
        text_in_pdf = self.validate_text_in_pdf(
            pdf_path,
            survey_models.TextPDFQuestionGroup.objects.get(
                question_group=self.question_groups[question_group_index],
                min_score=expected_min_score,
            ).text,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_1_0(self):
        """
        Test PDF text generation with question group 1 and score 0
        """
        self._test_pdf_text_generation(question_group_index=0, score=0)

    def test_generate_pdf_with_question_group_2_0(self):
        """
        Test PDF text generation with question group 2 and score 0
        """
        self._test_pdf_text_generation(question_group_index=1, score=0)

    def test_generate_pdf_with_question_group_3_0(self):
        """
        Test PDF text generation with question group 3 and score 0
        """
        self._test_pdf_text_generation(question_group_index=2, score=0)

    def test_generate_pdf_with_question_group_4_0(self):
        """
        Test PDF text generation with question group 4 and score 0
        """
        self._test_pdf_text_generation(question_group_index=3, score=0)

    def test_generate_pdf_with_question_group_5_0(self):
        """
        Test PDF text generation with question group 5 and score 0
        """
        self._test_pdf_text_generation(question_group_index=4, score=0)

    def test_generate_pdf_with_question_group_6_0(self):
        """
        Test PDF text generation with question group 6 and score 0
        """
        self._test_pdf_text_generation(question_group_index=5, score=0)

    def test_generate_pdf_with_question_group_7_0(self):
        """
        Test PDF text generation with question group 7 and score 0
        """
        self._test_pdf_text_generation(question_group_index=6, score=0)

    def test_generate_pdf_with_question_group_8_0(self):
        """
        Test PDF text generation with question group 8 and score 0
        """
        self._test_pdf_text_generation(question_group_index=7, score=0)

    def test_generate_pdf_with_question_group_9_0(self):
        """
        Test PDF text generation with question group 9 and score 0
        """
        self._test_pdf_text_generation(question_group_index=8, score=0)

    def test_generate_pdf_with_question_group_10_0(self):
        """
        Test PDF text generation with question group 10 and score 0
        """
        self._test_pdf_text_generation(question_group_index=9, score=0)

    def test_generate_pdf_with_question_group_11_0(self):
        """
        Test PDF text generation with question group 11 and score 0
        """
        self._test_pdf_text_generation(question_group_index=10, score=0)

    def test_generate_pdf_with_question_group_12_0(self):
        """
        Test PDF text generation with question group 12 and score 0
        """
        self._test_pdf_text_generation(question_group_index=11, score=0)

    def test_generate_pdf_with_question_group_13_0(self):
        """
        Test PDF text generation with question group 13 and score 0
        """
        self._test_pdf_text_generation(question_group_index=12, score=0)

    def test_generate_pdf_with_question_group_1_49(self):
        """
        Test PDF text generation with question group 1 and score 49
        """
        self._test_pdf_text_generation(question_group_index=0, score=49)

    def test_generate_pdf_with_question_group_2_49(self):
        """
        Test PDF text generation with question group 2 and score 49
        """
        self._test_pdf_text_generation(question_group_index=1, score=49)

    def test_generate_pdf_with_question_group_3_49(self):
        """
        Test PDF text generation with question group 3 and score 49
        """
        self._test_pdf_text_generation(question_group_index=2, score=49)

    def test_generate_pdf_with_question_group_4_49(self):
        """
        Test PDF text generation with question group 4 and score 49
        """
        self._test_pdf_text_generation(question_group_index=3, score=49)

    def test_generate_pdf_with_question_group_5_49(self):
        """
        Test PDF text generation with question group 5 and score 49
        """
        self._test_pdf_text_generation(question_group_index=4, score=49)

    def test_generate_pdf_with_question_group_6_49(self):
        """
        Test PDF text generation with question group 6 and score 49
        """
        self._test_pdf_text_generation(question_group_index=5, score=49)

    def test_generate_pdf_with_question_group_7_49(self):
        """
        Test PDF text generation with question group 7 and score 49
        """
        self._test_pdf_text_generation(question_group_index=6, score=49)

    def test_generate_pdf_with_question_group_8_49(self):
        """
        Test PDF text generation with question group 8 and score 49
        """
        self._test_pdf_text_generation(question_group_index=7, score=49)

    def test_generate_pdf_with_question_group_9_49(self):
        """
        Test PDF text generation with question group 9 and score 49
        """
        self._test_pdf_text_generation(question_group_index=8, score=49)

    def test_generate_pdf_with_question_group_10_49(self):
        """
        Test PDF text generation with question group 10 and score 49
        """
        self._test_pdf_text_generation(question_group_index=9, score=49)

    def test_generate_pdf_with_question_group_11_49(self):
        """
        Test PDF text generation with question group 11 and score 49
        """
        self._test_pdf_text_generation(question_group_index=10, score=49)

    def test_generate_pdf_with_question_group_12_49(self):
        """
        Test PDF text generation with question group 12 and score 49
        """
        self._test_pdf_text_generation(question_group_index=11, score=49)

    def test_generate_pdf_with_question_group_13_49(self):
        """
        Test PDF text generation with question group 13 and score 49
        """
        self._test_pdf_text_generation(question_group_index=12, score=49)

    def test_generate_pdf_with_question_group_1_50(self):
        """
        Test PDF text generation with question group 1 and score 50
        """
        self._test_pdf_text_generation(question_group_index=0, score=50)

    def test_generate_pdf_with_question_group_2_50(self):
        """
        Test PDF text generation with question group 2 and score 50
        """
        self._test_pdf_text_generation(question_group_index=1, score=50)

    def test_generate_pdf_with_question_group_3_50(self):
        """
        Test PDF text generation with question group 3 and score 50
        """
        self._test_pdf_text_generation(question_group_index=2, score=50)

    def test_generate_pdf_with_question_group_4_50(self):
        """
        Test PDF text generation with question group 4 and score 50
        """
        self._test_pdf_text_generation(question_group_index=3, score=50)

    def test_generate_pdf_with_question_group_5_50(self):
        """
        Test PDF text generation with question group 5 and score 50
        """
        self._test_pdf_text_generation(question_group_index=4, score=50)

    def test_generate_pdf_with_question_group_6_50(self):
        """
        Test PDF text generation with question group 6 and score 50
        """
        self._test_pdf_text_generation(question_group_index=5, score=50)

    def test_generate_pdf_with_question_group_7_50(self):
        """
        Test PDF text generation with question group 7 and score 50
        """
        self._test_pdf_text_generation(question_group_index=6, score=50)

    def test_generate_pdf_with_question_group_8_50(self):
        """
        Test PDF text generation with question group 8 and score 50
        """
        self._test_pdf_text_generation(question_group_index=7, score=50)

    def test_generate_pdf_with_question_group_9_50(self):
        """
        Test PDF text generation with question group 9 and score 50
        """
        self._test_pdf_text_generation(question_group_index=8, score=50)

    def test_generate_pdf_with_question_group_10_50(self):
        """
        Test PDF text generation with question group 10 and score 50
        """
        self._test_pdf_text_generation(question_group_index=9, score=50)

    def test_generate_pdf_with_question_group_11_50(self):
        """
        Test PDF text generation with question group 11 and score 50
        """
        self._test_pdf_text_generation(question_group_index=10, score=50)

    def test_generate_pdf_with_question_group_12_50(self):
        """
        Test PDF text generation with question group 12 and score 50
        """
        self._test_pdf_text_generation(question_group_index=11, score=50)

    def test_generate_pdf_with_question_group_13_50(self):
        """
        Test PDF text generation with question group 13 and score 50
        """
        self._test_pdf_text_generation(question_group_index=12, score=50)

    def test_generate_pdf_with_question_group_1_51(self):
        """
        Test PDF text generation with question group 1 and score 51
        """
        self._test_pdf_text_generation(question_group_index=0, score=51)

    def test_generate_pdf_with_question_group_2_51(self):
        """
        Test PDF text generation with question group 2 and score 51
        """
        self._test_pdf_text_generation(question_group_index=1, score=51)

    def test_generate_pdf_with_question_group_3_51(self):
        """
        Test PDF text generation with question group 3 and score 51
        """
        self._test_pdf_text_generation(question_group_index=2, score=51)

    def test_generate_pdf_with_question_group_4_51(self):
        """
        Test PDF text generation with question group 4 and score 51
        """
        self._test_pdf_text_generation(question_group_index=3, score=51)

    def test_generate_pdf_with_question_group_5_51(self):
        """
        Test PDF text generation with question group 5 and score 51
        """
        self._test_pdf_text_generation(question_group_index=4, score=51)

    def test_generate_pdf_with_question_group_6_51(self):
        """
        Test PDF text generation with question group 6 and score 51
        """
        self._test_pdf_text_generation(question_group_index=5, score=51)

    def test_generate_pdf_with_question_group_7_51(self):
        """
        Test PDF text generation with question group 7 and score 51
        """
        self._test_pdf_text_generation(question_group_index=6, score=51)

    def test_generate_pdf_with_question_group_8_51(self):
        """
        Test PDF text generation with question group 8 and score 51
        """
        self._test_pdf_text_generation(question_group_index=7, score=51)

    def test_generate_pdf_with_question_group_9_51(self):
        """
        Test PDF text generation with question group 9 and score 51
        """
        self._test_pdf_text_generation(question_group_index=8, score=51)

    def test_generate_pdf_with_question_group_10_51(self):
        """
        Test PDF text generation with question group 10 and score 51
        """
        self._test_pdf_text_generation(question_group_index=9, score=51)

    def test_generate_pdf_with_question_group_11_51(self):
        """
        Test PDF text generation with question group 11 and score 51
        """
        self._test_pdf_text_generation(question_group_index=10, score=51)

    def test_generate_pdf_with_question_group_12_51(self):
        """
        Test PDF text generation with question group 12 and score 51
        """
        self._test_pdf_text_generation(question_group_index=11, score=51)

    def test_generate_pdf_with_question_group_13_51(self):
        """
        Test PDF text generation with question group 13 and score 51
        """
        self._test_pdf_text_generation(question_group_index=12, score=51)

    def test_generate_pdf_with_question_group_1_69(self):
        """
        Test PDF text generation with question group 1 and score 69
        """
        self._test_pdf_text_generation(question_group_index=0, score=69)

    def test_generate_pdf_with_question_group_2_69(self):
        """
        Test PDF text generation with question group 2 and score 69
        """
        self._test_pdf_text_generation(question_group_index=1, score=69)

    def test_generate_pdf_with_question_group_3_69(self):
        """
        Test PDF text generation with question group 3 and score 69
        """
        self._test_pdf_text_generation(question_group_index=2, score=69)

    def test_generate_pdf_with_question_group_4_69(self):
        """
        Test PDF text generation with question group 4 and score 69
        """
        self._test_pdf_text_generation(question_group_index=3, score=69)

    def test_generate_pdf_with_question_group_5_69(self):
        """
        Test PDF text generation with question group 5 and score 69
        """
        self._test_pdf_text_generation(question_group_index=4, score=69)

    def test_generate_pdf_with_question_group_6_69(self):
        """
        Test PDF text generation with question group 6 and score 69
        """
        self._test_pdf_text_generation(question_group_index=5, score=69)

    def test_generate_pdf_with_question_group_7_69(self):
        """
        Test PDF text generation with question group 7 and score 69
        """
        self._test_pdf_text_generation(question_group_index=6, score=69)

    def test_generate_pdf_with_question_group_8_69(self):
        """
        Test PDF text generation with question group 8 and score 69
        """
        self._test_pdf_text_generation(question_group_index=7, score=69)

    def test_generate_pdf_with_question_group_9_69(self):
        """
        Test PDF text generation with question group 9 and score 69
        """
        self._test_pdf_text_generation(question_group_index=8, score=69)

    def test_generate_pdf_with_question_group_10_69(self):
        """
        Test PDF text generation with question group 10 and score 69
        """
        self._test_pdf_text_generation(question_group_index=9, score=69)

    def test_generate_pdf_with_question_group_11_69(self):
        """
        Test PDF text generation with question group 11 and score 69
        """
        self._test_pdf_text_generation(question_group_index=10, score=69)

    def test_generate_pdf_with_question_group_12_69(self):
        """
        Test PDF text generation with question group 12 and score 69
        """
        self._test_pdf_text_generation(question_group_index=11, score=69)

    def test_generate_pdf_with_question_group_13_69(self):
        """
        Test PDF text generation with question group 13 and score 69
        """
        self._test_pdf_text_generation(question_group_index=12, score=69)

    def test_generate_pdf_with_question_group_1_70(self):
        """
        Test PDF text generation with question group 1 and score 70
        """
        self._test_pdf_text_generation(question_group_index=0, score=70)

    def test_generate_pdf_with_question_group_2_70(self):
        """
        Test PDF text generation with question group 2 and score 70
        """
        self._test_pdf_text_generation(question_group_index=1, score=70)

    def test_generate_pdf_with_question_group_3_70(self):
        """
        Test PDF text generation with question group 3 and score 70
        """
        self._test_pdf_text_generation(question_group_index=2, score=70)

    def test_generate_pdf_with_question_group_4_70(self):
        """
        Test PDF text generation with question group 4 and score 70
        """
        self._test_pdf_text_generation(question_group_index=3, score=70)

    def test_generate_pdf_with_question_group_5_70(self):
        """
        Test PDF text generation with question group 5 and score 70
        """
        self._test_pdf_text_generation(question_group_index=4, score=70)

    def test_generate_pdf_with_question_group_6_70(self):
        """
        Test PDF text generation with question group 6 and score 70
        """
        self._test_pdf_text_generation(question_group_index=5, score=70)

    def test_generate_pdf_with_question_group_7_70(self):
        """
        Test PDF text generation with question group 7 and score 70
        """
        self._test_pdf_text_generation(question_group_index=6, score=70)

    def test_generate_pdf_with_question_group_8_70(self):
        """
        Test PDF text generation with question group 8 and score 70
        """
        self._test_pdf_text_generation(question_group_index=7, score=70)

    def test_generate_pdf_with_question_group_9_70(self):
        """
        Test PDF text generation with question group 9 and score 70
        """
        self._test_pdf_text_generation(question_group_index=8, score=70)

    def test_generate_pdf_with_question_group_10_70(self):
        """
        Test PDF text generation with question group 10 and score 70
        """
        self._test_pdf_text_generation(question_group_index=9, score=70)

    def test_generate_pdf_with_question_group_11_70(self):
        """
        Test PDF text generation with question group 11 and score 70
        """
        self._test_pdf_text_generation(question_group_index=10, score=70)

    def test_generate_pdf_with_question_group_12_70(self):
        """
        Test PDF text generation with question group 12 and score 70
        """
        self._test_pdf_text_generation(question_group_index=11, score=70)

    def test_generate_pdf_with_question_group_13_70(self):
        """
        Test PDF text generation with question group 13 and score 70
        """
        self._test_pdf_text_generation(question_group_index=12, score=70)

    def test_generate_pdf_with_question_group_1_71(self):
        """
        Test PDF text generation with question group 1 and score 71
        """
        self._test_pdf_text_generation(question_group_index=0, score=71)

    def test_generate_pdf_with_question_group_2_71(self):
        """
        Test PDF text generation with question group 2 and score 71
        """
        self._test_pdf_text_generation(question_group_index=1, score=71)

    def test_generate_pdf_with_question_group_3_71(self):
        """
        Test PDF text generation with question group 3 and score 71
        """
        self._test_pdf_text_generation(question_group_index=2, score=71)

    def test_generate_pdf_with_question_group_4_71(self):
        """
        Test PDF text generation with question group 4 and score 71
        """
        self._test_pdf_text_generation(question_group_index=3, score=71)

    def test_generate_pdf_with_question_group_5_71(self):
        """
        Test PDF text generation with question group 5 and score 71
        """
        self._test_pdf_text_generation(question_group_index=4, score=71)

    def test_generate_pdf_with_question_group_6_71(self):
        """
        Test PDF text generation with question group 6 and score 71
        """
        self._test_pdf_text_generation(question_group_index=5, score=71)

    def test_generate_pdf_with_question_group_7_71(self):
        """
        Test PDF text generation with question group 7 and score 71
        """
        self._test_pdf_text_generation(question_group_index=6, score=71)

    def test_generate_pdf_with_question_group_8_71(self):
        """
        Test PDF text generation with question group 8 and score 71
        """
        self._test_pdf_text_generation(question_group_index=7, score=71)

    def test_generate_pdf_with_question_group_9_71(self):
        """
        Test PDF text generation with question group 9 and score 71
        """
        self._test_pdf_text_generation(question_group_index=8, score=71)

    def test_generate_pdf_with_question_group_10_71(self):
        """
        Test PDF text generation with question group 10 and score 71
        """
        self._test_pdf_text_generation(question_group_index=9, score=71)

    def test_generate_pdf_with_question_group_11_71(self):
        """
        Test PDF text generation with question group 11 and score 71
        """
        self._test_pdf_text_generation(question_group_index=10, score=71)

    def test_generate_pdf_with_question_group_12_71(self):
        """
        Test PDF text generation with question group 12 and score 71
        """
        self._test_pdf_text_generation(question_group_index=11, score=71)

    def test_generate_pdf_with_question_group_13_71(self):
        """
        Test PDF text generation with question group 13 and score 71
        """
        self._test_pdf_text_generation(question_group_index=12, score=71)

    def test_generate_pdf_with_question_group_1_99(self):
        """
        Test PDF text generation with question group 1 and score 99
        """
        self._test_pdf_text_generation(question_group_index=0, score=99)

    def test_generate_pdf_with_question_group_2_99(self):
        """
        Test PDF text generation with question group 2 and score 99
        """
        self._test_pdf_text_generation(question_group_index=1, score=99)

    def test_generate_pdf_with_question_group_3_99(self):
        """
        Test PDF text generation with question group 3 and score 99
        """
        self._test_pdf_text_generation(question_group_index=2, score=99)

    def test_generate_pdf_with_question_group_4_99(self):
        """
        Test PDF text generation with question group 4 and score 99
        """
        self._test_pdf_text_generation(question_group_index=3, score=99)

    def test_generate_pdf_with_question_group_5_99(self):
        """
        Test PDF text generation with question group 5 and score 99
        """
        self._test_pdf_text_generation(question_group_index=4, score=99)

    def test_generate_pdf_with_question_group_6_99(self):
        """
        Test PDF text generation with question group 6 and score 99
        """
        self._test_pdf_text_generation(question_group_index=5, score=99)

    def test_generate_pdf_with_question_group_7_99(self):
        """
        Test PDF text generation with question group 7 and score 99
        """
        self._test_pdf_text_generation(question_group_index=6, score=99)

    def test_generate_pdf_with_question_group_8_99(self):
        """
        Test PDF text generation with question group 8 and score 99
        """
        self._test_pdf_text_generation(question_group_index=7, score=99)

    def test_generate_pdf_with_question_group_9_99(self):
        """
        Test PDF text generation with question group 9 and score 99
        """
        self._test_pdf_text_generation(question_group_index=8, score=99)

    def test_generate_pdf_with_question_group_10_99(self):
        """
        Test PDF text generation with question group 10 and score 99
        """
        self._test_pdf_text_generation(question_group_index=9, score=99)

    def test_generate_pdf_with_question_group_11_99(self):
        """
        Test PDF text generation with question group 11 and score 99
        """
        self._test_pdf_text_generation(question_group_index=10, score=99)

    def test_generate_pdf_with_question_group_12_99(self):
        """
        Test PDF text generation with question group 12 and score 99
        """
        self._test_pdf_text_generation(question_group_index=11, score=99)

    def test_generate_pdf_with_question_group_13_99(self):
        """
        Test PDF text generation with question group 13 and score 99
        """
        self._test_pdf_text_generation(question_group_index=12, score=99)

    def test_generate_pdf_with_question_group_1_100(self):
        """
        Test PDF text generation with question group 1 and score 100
        """
        self._test_pdf_text_generation(question_group_index=0, score=100)

    def test_generate_pdf_with_question_group_2_100(self):
        """
        Test PDF text generation with question group 2 and score 100
        """
        self._test_pdf_text_generation(question_group_index=1, score=100)

    def test_generate_pdf_with_question_group_3_100(self):
        """
        Test PDF text generation with question group 3 and score 100
        """
        self._test_pdf_text_generation(question_group_index=2, score=100)

    def test_generate_pdf_with_question_group_4_100(self):
        """
        Test PDF text generation with question group 4 and score 100
        """
        self._test_pdf_text_generation(question_group_index=3, score=100)

    def test_generate_pdf_with_question_group_5_100(self):
        """
        Test PDF text generation with question group 5 and score 100
        """
        self._test_pdf_text_generation(question_group_index=4, score=100)

    def test_generate_pdf_with_question_group_6_100(self):
        """
        Test PDF text generation with question group 6 and score 100
        """
        self._test_pdf_text_generation(question_group_index=5, score=100)

    def test_generate_pdf_with_question_group_7_100(self):
        """
        Test PDF text generation with question group 7 and score 100
        """
        self._test_pdf_text_generation(question_group_index=6, score=100)

    def test_generate_pdf_with_question_group_8_100(self):
        """
        Test PDF text generation with question group 8 and score 100
        """
        self._test_pdf_text_generation(question_group_index=7, score=100)

    def test_generate_pdf_with_question_group_9_100(self):
        """
        Test PDF text generation with question group 9 and score 100
        """
        self._test_pdf_text_generation(question_group_index=8, score=100)

    def test_generate_pdf_with_question_group_10_100(self):
        """
        Test PDF text generation with question group 10 and score 100
        """
        self._test_pdf_text_generation(question_group_index=9, score=100)

    def test_generate_pdf_with_question_group_11_100(self):
        """
        Test PDF text generation with question group 11 and score 100
        """
        self._test_pdf_text_generation(question_group_index=10, score=100)

    def test_generate_pdf_with_question_group_12_100(self):
        """
        Test PDF text generation with question group 12 and score 100
        """
        self._test_pdf_text_generation(question_group_index=11, score=100)

    def test_generate_pdf_with_question_group_13_100(self):
        """
        Test PDF text generation with question group 13 and score 100
        """
        self._test_pdf_text_generation(question_group_index=12, score=100)


class GenerateNextReportTextPDFSummaryTestCase(GenerateNextReportBase):
    """
    Test PDF text generation
    """

    def setUp(self):
        """Set up test data"""

        # setup initial data from parent class
        super().setUp()

        # Create apo data
        self.invitation_code = "test"
        self.data = {
            "invitation_code": self.invitation_code,
            "survey_id": 1,
            "participant": {
                "email": "test@test.com",
                "name": "Test User",
                "gender": "m",
                "birth_range": "1946-1964",
                "position": "director",
            },
            "answers": [],
        }
        self.endpoint = "/api/response/"

        # Create company with invitation code
        self.company = self.create_company(invitation_code=self.invitation_code)

        # tests data
        self.summary_types = ["CD", "TN", "CS", "IP", "TMA", "EDC"]

    def __validate_title_and_text(self, pdf_path: str, summary_type: str, score: int):
        """
        Validate title and text in PDF

        Args:
            pdf_path(str): Path to the pdf file
            summary_type(str): Type of summary
            score(int): Participant score
        """

        text_entry_all = survey_models.TextPDFSummary.objects.filter(
            paragraph_type=summary_type, min_score__lte=score
        ).order_by("min_score")

        for text_entry in text_entry_all:
            print(
                f"DEBUG: TextPDFSummary for type={summary_type}, score={text_entry.min_score}: {text_entry.text}"
            )

        # Find the text with the highest min_score that is less than or equal to the score
        text_entry = (
            survey_models.TextPDFSummary.objects.filter(
                paragraph_type=summary_type, min_score__lte=score
            )
            .order_by("min_score")
            .last()
        )

        # Set min score
        if not text_entry:
            text_entry = (
                survey_models.TextPDFSummary.objects.filter(paragraph_type=summary_type)
                .order_by("min_score")
                .first()
            )

        text_summary = text_entry.text
        title, text = text_summary.split("|")
        title = title.strip()
        text = text.strip()

        # Validate title in pdf
        title_in_pdf = self.validate_text_in_pdf(pdf_path, title)
        if not title_in_pdf:
            print(f"DEBUG: Title '{title}' not found in PDF for score {score}")
            # Debug PDF content
            with open(pdf_path, "rb") as f:
                reader = PdfReader(f)
                pdf_text = ""
                for page in reader.pages:
                    pdf_text += page.extract_text()

            def normalize(s):
                s = s.lower()
                s = re.sub(r"\s+", " ", s)
                return s.strip()

            norm_pdf = normalize(pdf_text)
            norm_title = normalize(title)
            print(f"DEBUG: Normalized Title: '{norm_title}'")
            print(f"DEBUG: Normalized PDF Content (subset): '{norm_pdf[:200]}...'")
            if norm_title in norm_pdf:
                print(
                    "DEBUG: Title IS in normalized PDF! validation_text_in_pdf might be creating a new instance or normalized differently?"
                )
            else:
                print("DEBUG: Title really NOT in normalized PDF.")

        self.assertTrue(
            title_in_pdf, f"Title '{title}' not found in PDF for score {score}"
        )

        # Validate text in pdf (optional, based on observed code)
        if text:
            text_in_pdf = self.validate_text_in_pdf(pdf_path, text)
            if not text_in_pdf:
                print(f"DEBUG: Text body not found in PDF for score {score}")
            self.assertTrue(
                text_in_pdf, f"Text body not found in PDF for score {score}"
            )

    def _run_test_with_score(self, score, validation_score=None):
        if validation_score is None:
            validation_score = score

        for i, summary_type in enumerate(self.summary_types):
            # Update participant name to ensure unique PDF filename
            # This is crucial because create_get_pdf relies on finding a NEW file
            self.participant.name = (
                f"Test User {score} {summary_type} {i} {random.randint(10000, 99999)}"
            )
            self.participant.save()

            selected_options = self.get_selected_options(score=score)
            self.create_report(
                options=selected_options, invitation_code=self.invitation_code
            )

            # create and get pdf
            try:
                pdf_path = self.create_get_pdf()
            except AssertionError as e:
                print(f"DEBUG: create_get_pdf failed for {score}/{summary_type}: {e}")
                # List files in dir to see what happened
                pdf_folder = os.path.join(settings.BASE_DIR, "media", "reports")
                if os.path.exists(pdf_folder):
                    print(f"DEBUG: Files in {pdf_folder}: {os.listdir(pdf_folder)}")
                raise

            # Validate text in pdf
            self.__validate_title_and_text(pdf_path, summary_type, validation_score)

    def test_generate_pdf_summary_with_100(self):
        """
        Test PDF summary text generation with score 100
        """
        self._run_test_with_score(100)

    def test_generate_pdf_summary_with_99(self):
        """
        Test PDF summary text generation with score 99
        """
        # 99% score with 10 questions results in 90%
        self._run_test_with_score(99, validation_score=90)

    def test_generate_pdf_summary_with_80(self):
        """
        Test PDF summary text generation with score 80
        """
        self._run_test_with_score(80)

    def test_generate_pdf_summary_with_79(self):
        """
        Test PDF summary text generation with score 79
        """
        # 79% score with 10 questions results in 70%
        self._run_test_with_score(79, validation_score=70)

    def test_generate_pdf_summary_with_50(self):
        """
        Test PDF summary text generation with score 50
        """
        self._run_test_with_score(50)

    def test_generate_pdf_summary_with_49(self):
        """
        Test PDF summary text generation with score 49
        """
        # 49% score with 10 questions results in 40%
        self._run_test_with_score(49, validation_score=40)

    def test_generate_pdf_summary_with_0(self):
        """
        Test PDF summary text generation with score 0
        """
        self._run_test_with_score(0)


class CreateReportsDownloadFileCommandTest(TestSurveyModelBase, APITestCase):
    """
    Test suite for create_reports_download_file command
    """

    def setUp(self):
        super().setUp()

        # Load data
        call_command("apps_loaddata")
        call_command("initial_loaddata")

        # Login to client with session
        username = "test_user"
        password = "test_pass"
        User.objects.create_superuser(
            username=username,
            email="test@gmail.com",
            password=password,
        )
        self.client.login(username=username, password=password)

        # Ensure temp dir exists or is clean for tests
        self.temp_dir = os.path.join(settings.BASE_DIR, "media", "temp", "zips")
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir, exist_ok=True)

        # Create basic data
        self.company = self.create_company()
        self.participant = self.create_participant(company=self.company)
        self.survey = survey_models.Survey.objects.get(id=1)

        # Create a dummy PDF file for testing
        self.dummy_pdf_content = b"%PDF-1.4 dummy content"
        self.dummy_pdf_name = "test_report.pdf"

    def tearDown(self):
        # Cleanup temp dir
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        super().tearDown()

    def create_dummy_report_with_pdf(self):
        report = self.create_report()
        report.pdf_file = SimpleUploadedFile(
            self.dummy_pdf_name, self.dummy_pdf_content, content_type="application/pdf"
        )
        report.status = "completed"
        report.save()
        return report

    def create_reports_download(self, reports=None):
        if reports is None:
            reports = []
        download = survey_models.ReportsDownload.objects.create(status="pending")
        if reports:
            download.reports.set(reports)
        return download

    def test_no_pending_downloads(self):
        """Test command when there are no pending downloads"""
        # Ensure no pending downloads exist
        survey_models.ReportsDownload.objects.all().delete()

        with patch("sys.stdout.write") as mock_stdout:
            call_command("create_reports_download_file")
            # We expect a message saying no reports to download
            # Note: Checking exact string might depend on implementation details
            pass

        # Verify nothing changed
        self.assertEqual(
            survey_models.ReportsDownload.objects.filter(status="pending").count(), 0
        )

    @patch("requests.get")
    def test_success_single_report(self, mock_get):
        """Test successful zip generation for a single report"""
        # Configure mock for model creation (n8n webhook) AND pdf download
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = self.dummy_pdf_content
        mock_response.json.return_value = {"success": True}
        mock_get.return_value = mock_response

        report = self.create_dummy_report_with_pdf()
        download = self.create_reports_download([report])

        # Verify creation didn't fail
        self.assertEqual(download.status, "pending", download.logs)

        call_command("create_reports_download_file")

        download.refresh_from_db()
        self.assertEqual(download.status, "completed", download.logs)
        self.assertTrue(download.zip_file)
        self.assertTrue(download.zip_file.name.endswith(".zip"))
        self.assertIn("completed", download.logs)

    @patch("requests.get")
    def test_success_multiple_reports(self, mock_get):
        """Test successful zip generation for multiple reports"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = self.dummy_pdf_content
        mock_response.json.return_value = {"success": True}
        mock_get.return_value = mock_response

        report1 = self.create_dummy_report_with_pdf()
        report2 = self.create_dummy_report_with_pdf()
        download = self.create_reports_download([report1, report2])

        call_command("create_reports_download_file")

        download.refresh_from_db()
        self.assertEqual(download.status, "completed", download.logs)
        self.assertTrue(download.zip_file)

        # Requests: 1 for model creation, 2 for PDFs
        self.assertEqual(mock_get.call_count, 3)

    @patch("requests.get")
    def test_missing_pdf_file_in_report(self, mock_get):
        """Test handling when a report is missing the PDF file"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = self.dummy_pdf_content
        mock_response.json.return_value = {"success": True}
        mock_get.return_value = mock_response

        # Report with PDF
        report1 = self.create_dummy_report_with_pdf()
        # Report without PDF
        report2 = self.create_report()
        report2.status = "completed"
        report2.save()

        download = self.create_reports_download([report1, report2])

        call_command("create_reports_download_file")

        download.refresh_from_db()
        self.assertEqual(download.status, "completed", download.logs)
        # Should still have a zip file (containing the available PDF)
        self.assertTrue(download.zip_file)

        # Check logs for missing PDF message
        self.assertIn(f"Report {report2.id} has no pdf file", download.logs)

    @patch("requests.get")
    def test_download_error_404(self, mock_get):
        """Test handling when PDF download fails"""
        # We need successful creation, then 404 for download

        # Response for creation
        creation_response = MagicMock()
        creation_response.status_code = 200
        creation_response.json.return_value = {"success": True}

        # Response for download
        download_response = MagicMock()
        download_response.status_code = 404

        mock_get.side_effect = [creation_response, download_response]

        report = self.create_dummy_report_with_pdf()
        download = self.create_reports_download([report])

        self.assertEqual(download.status, "pending")

        call_command("create_reports_download_file")

        download.refresh_from_db()
        # Command should complete even if one file fails (it logs error)
        self.assertEqual(download.status, "completed", download.logs)
        self.assertIn(f"Failed to download pdf file", download.logs)

    @patch("zipfile.ZipFile")
    @patch("requests.get")
    def test_general_exception(self, mock_get, mock_zip):
        """Test handling of unexpected exceptions"""
        # Creation success
        creation_response = MagicMock()
        creation_response.status_code = 200
        creation_response.json.return_value = {"success": True}

        # Download success
        download_response = MagicMock()
        download_response.status_code = 200
        download_response.content = self.dummy_pdf_content

        mock_get.side_effect = [creation_response, download_response]

        report = self.create_dummy_report_with_pdf()
        download = self.create_reports_download([report])

        # Mock an exception during zip creation
        mock_zip.side_effect = Exception("Boom!")

        call_command("create_reports_download_file")

        download.refresh_from_db()
        self.assertEqual(download.status, "error", download.logs)
        self.assertIn("Error: Boom!", download.logs)

    @patch("requests.get")
    def test_duplicate_participant_names_reproduce_crash(self, mock_get):
        """
        Test that duplicate participant names currently cause a crash
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = self.dummy_pdf_content
        mock_response.json.return_value = {"success": True}
        mock_get.return_value = mock_response

        # Create 2 reports
        report1 = self.create_dummy_report_with_pdf()
        report2 = self.create_dummy_report_with_pdf()

        # Ensure they have the same participant name
        p1 = report1.participant
        p2 = report2.participant
        p2.name = p1.name
        p2.save()

        download = self.create_reports_download([report1, report2])

        # This should currently fail (status error) or crash the command
        call_command("create_reports_download_file")

        download.refresh_from_db()

        # If bug exists, this will fail assertion as status will be 'error'
        # with logs containing 'No such file or directory'
        self.assertEqual(
            download.status,
            "completed",
            f"Expected completed, got {download.status}. Logs: {download.logs}",
        )


from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from survey.models import FormProgress, Survey


class DeleteExpiredProgressCommandTestCase(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(name="Test Survey")
        self.email = "test@example.com"

        # Create expired record
        self.expired = FormProgress.objects.create(
            email="expired@example.com", survey=self.survey, current_screen=1, data={}
        )
        self.expired.expires_at = timezone.now() - timedelta(days=1)
        self.expired.save()

        # Create active record
        self.active = FormProgress.objects.create(
            email="active@example.com", survey=self.survey, current_screen=1, data={}
        )
        # Default expiration is in future, so it should stay

    def test_delete_expired(self):
        """Test that expired records are deleted and active ones remain"""
        call_command("delete_expired_progress")

        self.assertFalse(FormProgress.objects.filter(pk=self.expired.pk).exists())
        self.assertTrue(FormProgress.objects.filter(pk=self.active.pk).exists())
