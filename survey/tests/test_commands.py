import os
import re
import json
import random
from time import sleep

from django.core.management import call_command
from django.conf import settings
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status

from core.tests_base.test_models import TestSurveyModelBase
from survey import models as survey_models
from utils.media import get_media_url
from utils.survey_calcs import SurveyCalcs

import requests
from PyPDF2 import PdfReader
from playwright.sync_api import sync_playwright


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


class GenerateNextReportTextPDFQuestionGroupTestCase(GenerateNextReportBase):
    """
    Test PDF text generation
    """

    def setUp(self):
        """Set up test data"""

        # Load initial data
        call_command("apps_loaddata")
        call_command("initial_loaddata")
        self.questions, self.options = self.__create_question_and_options()

        # Create user and login
        username = "test_user"
        password = "test_pass"
        User.objects.create_superuser(
            username=username,
            email="test@gmail.com",
            password=password,
        )
        self.client.login(username=username, password=password)

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
        self.company = self.create_company(invitation_code=self.invitation_code)
        self.participant = self.create_participant(company=self.company)
        self.question_groups = survey_models.QuestionGroup.objects.all()
        self.endpoint = "/api/response/"

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

    def __get_selected_options(self, score: int) -> list[int]:
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

    def validate_text_in_pdf(self, pdf_path: str, text: str, page: int):
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
        with open(pdf_path, "rb") as f:
            pdf_reader = PdfReader(f)
            page_text = pdf_reader.pages[page].extract_text()

        print(page_text)

        # Validate text in pdf
        # Normalize both texts:
        def normalize(s):
            s = s.lower()  # To lowercase
            s = re.sub(r"\s+", " ", s)  # Replace multiple spaces/line breaks with one
            s = s.strip()  # Remove leading/trailing spaces
            return s

        normalized_text = normalize(text)
        normalized_page = normalize(page_text)

        # Check if text is in pdf
        return normalized_text in normalized_page

    def test_generate_pdf_with_question_group_1_50(self):
        """
        Test PDF text generation with question group 1 and score 50
        """

        selected_options = self.__get_selected_options(score=49)
        self.create_report(
            options=selected_options, invitation_code=self.invitation_code
        )

        # create and get pdf
        pdf_path = self.create_get_pdf()

        # Validate text in pdf
        text_in_pdf = self.validate_text_in_pdf(
            pdf_path,
            "Tu evaluación indica que aún hay áreas de oportunidad en cuanto a tu comprensión y aplicación de conceptos clave relacionados con la alfabetización tecnológica. Aunque reconoces la importancia de la tecnología en el entorno organizacional, es necesario que profundices en aspectos clave que iremos ampliando en este reporte. Te recomiendo que comiences por familiarizarte con las herramientas digitales fundamentales, participando en grupos especializados o accediendo a recursos prácticos que te permitan comprender cómo estos aspectos tecnológicos se aplican en los contextos empresariales actuales. Un enfoque adicional podría ser el desarrollo de tu pensamiento crítico frente a las tecnologías, lo cual te ayudará a tomar decisiones más informadas y a evaluar los riesgos asociados con su implementación. Al avanzar en estos puntos, mejorarás tu capacidad para liderar de manera eficaz en un mundo cada vez más digitalizado.",
            4,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_1_70(self):
        """
        Test PDF text generation with question group 1 and score 70
        """

        selected_options = self.__get_selected_options(score=69)
        self.create_report(
            options=selected_options, invitation_code=self.invitation_code
        )

        # create and get pdf
        pdf_path = self.create_get_pdf()

        # Validate text in pdf
        text_in_pdf = self.validate_text_in_pdf(
            pdf_path,
            "Tu evaluación sugiere que tienes un manejo adecuado de los conceptos fundamentales de la alfabetización tecnológica, aunque aún hay margen para profundizar en aspectos clave. Conoces la importancia de la tecnología y su impacto organizacional, te recomendaría que amplíes tu comprensión sobre cómo implementar herramientas avanzadas, como la inteligencia artificial, para mejorar procesos y tomar decisiones más estratégicas. Además, es importante que refuerces tus conocimientos sobre el cumplimiento de regulaciones y las mejores prácticas para proteger los datos organizacionales. Te sugiero que busques oportunidades para fortalecer tu capacidad de evaluar nuevas tecnologías y sus aplicaciones a nivel estratégico. Continuar aprendiendo sobre las tendencias emergentes te permitirá estar mejor preparado para liderar la innovación y gestionar el cambio dentro de tu organización.",
            4,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_1_100(self):
        """
        Test PDF text generation with question group 1 and score 100
        """

        selected_options = self.__get_selected_options(score=99)
        self.create_report(
            options=selected_options, invitation_code=self.invitation_code
        )

        # create and get pdf
        pdf_path = self.create_get_pdf()

        # Validate text in pdf
        text_in_pdf = self.validate_text_in_pdf(
            pdf_path,
            "Tu evaluación refleja un conocimiento sólido y avanzado sobre los aspectos clave de la alfabetización tecnológica, lo cual es una fortaleza significativa en tu perfil profesional. Comprendes bien las implicaciones y aplicaciones de tecnologías, lo que te permite tomar decisiones informadas y estratégicas en tu organización. No obstante, es recomendable que sigas profundizando en áreas emergentes, como la automatización de procesos y la cadena de bloques, para mantenerte a la vanguardia de las innovaciones tecnológicas. También podrías centrarte en expandir tu capacidad para fomentar una cultura digital dentro de tu equipo, asegurando que todos estén alineados con las nuevas herramientas y tecnologías. Si continúas desarrollando tus habilidades en la gestión de riesgos tecnológicos y el cumplimiento de normativas globales de seguridad, podrás fortalecer aún más tu liderazgo digital y asegurar que tu organización se mantenga competitiva a largo plazo.",
            4,
        )

        self.assertTrue(text_in_pdf)


class GenerateNextReportTextPDFSummaryTestCase(GenerateNextReportBase):
    """
    Test PDF text generation
    """

    def setUp(self):
        """Set up test data"""
        super().setUp(
            endpoint="/api/response/", restricted_get=True, restricted_post=False
        )

        # Load initial data
        call_command("apps_loaddata")
        call_command("initial_loaddata")
        self.questions, self.options = self.__create_question_and_options()

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
        self.company = self.create_company(invitation_code=self.invitation_code)
        self.participant = self.create_participant(company=self.company)
        self.question_groups = survey_models.QuestionGroup.objects.all()
        self.endpoint = "/api/response/"

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

    def __get_selected_options(self, score: int) -> list[int]:
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

    def validate_text_in_pdf(self, pdf_path: str, text: str, page: int):
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
        with open(pdf_path, "rb") as f:
            pdf_reader = PdfReader(f)
            page_text = pdf_reader.pages[page].extract_text()

        return text in page_text
