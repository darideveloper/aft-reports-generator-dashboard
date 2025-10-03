import os
import math
import json
import random
from time import sleep

from django.core.management import call_command
from django.conf import settings
from rest_framework import status

from core.tests_base.test_models import TestSurveyModelBase
from survey import models as survey_models
from utils.media import get_media_url
from utils.survey_calcs import SurveyCalcs

import requests
from PyPDF2 import PdfReader
from playwright.sync_api import sync_playwright


class GenerateNextReportBase(TestSurveyModelBase):
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
        self.report = self.create_report(
            survey=self.survey, participant=self.participant
        )

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
            reports.append(
                self.create_report(survey=self.survey, participant=self.participant)
            )

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

        call_command("generate_next_report")

        # Validate report data
        self.validate_report(self.report)

    def test_no_pending_reports(self):
        """
        Test with no pending reports
        Expect:
            - The command should do nothing (skip all reports)
        """

        # Delete initial reports
        survey_models.Report.objects.all().delete()

        # Create 2 reports in processing status
        reports = []
        for _ in range(2):
            reports.append(
                self.create_report(
                    survey=self.survey,
                    participant=self.participant,
                    status="processing",
                )
            )

        call_command("generate_next_report")

        # Validate no reports are ready to be processed or completed
        self.assertEqual(
            survey_models.Report.objects.filter(status="pending").count(), 0
        )
        self.assertEqual(
            survey_models.Report.objects.filter(status="completed").count(), 0
        )
        self.assertEqual(survey_models.Report.objects.filter(status="error").count(), 0)


class GenerateNextReportQuestionGroupTestCase(GenerateNextReportBase):
    """
    Test pdf report data is generated correctly (question group totals)
    """

    def test_totals_100(self):
        """
        Validate question group totals are calculated and saved
        (100% of the questions are correct)
        """

        # Create report question group totals data
        survey, options, question_groups = (
            self.create_report_question_group_totals_data()
        )

        # set CORRECT andser to each question
        selected_options = options.filter(points=1)
        for option in selected_options:
            self.create_answer(participant=self.participant, question_option=option)

        # Create a report
        call_command("generate_next_report")

        # Get report question group totals
        report_question_group_totals = []
        for question_group in question_groups:
            report_question_group_totals.append(
                survey_models.ReportQuestionGroupTotal.objects.get(
                    report=self.report, question_group=question_group
                )
            )

        # Validate report question group totals
        for report_question_group_total in report_question_group_totals:

            # Validate aprox value
            self.assertIsNotNone(report_question_group_total.total)
            self.assertEqual(report_question_group_total.total, 100)

        # Validate final score (2 question groups are 0)
        self.report.refresh_from_db()
        self.assertEqual(self.report.total, 100)

    def test_totals_50(self):
        """
        Validate question group totals are calculated and saved
        (50% of the questions are correct)
        """

        # Generate initial data
        survey, options, question_groups = (
            self.create_report_question_group_totals_data()
        )

        # select 50% of the options ins each question group
        for question_group in question_groups:
            selected_options = options.filter(
                points=1, question__question_group=question_group
            )
            selected_options = selected_options[: len(selected_options) // 2]
            for option in selected_options:
                self.create_answer(participant=self.participant, question_option=option)

        # Create a report
        call_command("generate_next_report")

        # Get report question group totals
        report_question_group_totals = []
        for question_group in question_groups:
            report_question_group_totals.append(
                survey_models.ReportQuestionGroupTotal.objects.get(
                    report=self.report, question_group=question_group
                )
            )

        # Validate report question group totals (only 2 with answers)
        for report_question_group_total in report_question_group_totals:
            self.assertEqual(report_question_group_total.total, 50)

        # Validate final score (2 question groups are 0)
        self.report.refresh_from_db()
        self.assertEqual(self.report.total, 50)

    def test_totals_0(self):
        """
        Validate question group totals are calculated and saved
        (0% of the questions are correct)
        """

        # Generate initial data
        survey, options, question_groups = (
            self.create_report_question_group_totals_data()
        )

        # select all incorrect options
        selected_options = options.filter(points=0)
        for option in selected_options:
            self.create_answer(participant=self.participant, question_option=option)

        # Create a report
        call_command("generate_next_report")

        # Get report question group totals
        report_question_group_totals = []
        for question_group in question_groups:
            report_question_group_totals.append(
                survey_models.ReportQuestionGroupTotal.objects.get(
                    report=self.report, question_group=question_group
                )
            )

        # Validate report question group totals
        for report_question_group_total in report_question_group_totals:
            self.assertEqual(report_question_group_total.total, 0)

        # Validate final score (2 question groups are 0)
        self.report.refresh_from_db()
        self.assertEqual(self.report.total, 0)

    def test_total_is_rounded(self):
        """
        Validate total is rounded to 2 decimal places
        """

        # Generate initial data
        survey, options, question_groups = (
            self.create_report_question_group_totals_data()
        )

        # Change wight of first question group to 33.33333
        question_groups[0].survey_percentage = 33.33333
        question_groups[0].save()

        # select one answer correct and one answer incorrect
        selected_options = [
            options[0],  # question 1, yes
            options[2],  # question 2, yes
            options[4],  # question 3, yes
            options[6],  # question 4, yes
        ]

        for option in selected_options:
            self.create_answer(participant=self.participant, question_option=option)

        # Create a report
        call_command("generate_next_report")

        # Validate total is rounded to 2 decimal places
        self.report.refresh_from_db()
        decimals = str(self.report.total).split(".")[1]
        self.assertEqual(len(decimals), 2)


class GenerateNextReportBellChartTestCase(GenerateNextReportBase):
    """
    Test pdf report data is generated correctly (bell chart)
    """

    def test_manual_check(self):
        """
        Validate bell chart data is generated correctly (manually user check required)
        """

        company_1 = self.participant.company
        company_2 = self.create_company()

        # Simillate responses
        _, options, _ = self.create_report_question_group_totals_data()
        score = 80
        selected_options_num = score * len(options) / 100
        selected_options = options[: int(selected_options_num)]
        
        for option in selected_options:
            self.create_answer(participant=self.participant, question_option=option)
        self.create_report(survey=self.survey, participant=self.participant)

        # Create a random number of reports with random score from 40 to 90
        # set random company in each one
        for _ in range(random.randint(100, 200)):
            report = self.create_report(
                survey=self.survey,
                participant=self.create_participant(company=company_1),
            )
            report.total = random.randint(40, 90)
            report.save()

        for _ in range(random.randint(100, 200)):
            report = self.create_report(
                survey=self.survey,
                participant=self.create_participant(company=company_2),
            )
            report.total = random.randint(30, 70)
            report.save()

        # create and get pdf
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

    def __create_report_with_score(self, score: int = 100):
        """
        Create questions and options, and set single and correct answer
        In order to asy generate an specific final score.
        Example: score = 50, 2 questions created and 1 correct answer.
        Finally create a report with the score.

        Args:
            score: Final score to generate

        """
        
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
        correct_answers = math.floor(len(options) * score / 100)

        # Set required correct answers
        for question_index in range(correct_answers):
            self.create_answer(
                participant=self.participant, question_option=options[question_index]
            )

        self.create_report(survey=self.survey, participant=self.participant)

    def __create_other_100_reports(self):
        """
        Create 100 reports with scores from score 0 to 100
        """
        for score in range(0, 100):
            report = self.create_report(
                survey=self.survey,
                participant=self.create_participant(company=self.participant.company),
            )
            report.total = score
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
        # Setup data
        self.__create_report_with_score(score=score)
        self.__create_other_100_reports()

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

        self.question_groups = survey_models.QuestionGroup.objects.all().order_by(
            "survey_index"
        )
        self.question_groups_totals = {
            question_group.id: [] for question_group in self.question_groups
        }

        # Create data for 2 participants
        for _ in range(2):
            # Create participant and report
            participant = self.create_participant(company=self.company)
            report = self.create_report(survey=self.survey, participant=participant)

            # Create question groups and set totals
            for question_group in self.question_groups:
                # Calculate and save total
                total = random.randint(0, 100)
                self.question_groups_totals[question_group.id].append(total)

                self.create_report_question_group_total(
                    report=report,
                    question_group=question_group,
                    total=total,
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
        # Validate reference line as avg
        question_groups_totals_current = self.question_groups_totals[question_group_id]
        question_groups_totals_avg = sum(question_groups_totals_current) / len(
            question_groups_totals_current
        )
        return question_groups_totals_avg

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
                self.assertEqual(
                    question_group_json["promedio"], question_group.goal_rate
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