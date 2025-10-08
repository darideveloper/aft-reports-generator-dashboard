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

    def test_generate_pdf_with_question_group_2_50(self):
        """
        Test PDF text generation with question group 2 and score 50
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
            "Tu evaluación muestra que aún hay áreas importantes en las que necesitas mejorar tu comprensión de la evolución tecnológica y su impacto en la vida humana. Aunque comprendes algunos de los desarrollos clave, te falta una conexión más profunda sobre cómo estas tecnologías han transformado los diferentes sectores de la sociedad. Te sugiero que te enfoques en estudiar más detalladamente los desarrollos tecnológicos recientes, como la inteligencia artificial y sobre todo cómo éstos han cambiado las industrias y la vida cotidiana. Para mejorar tu nivel de conocimiento, te recomiendo buscar recursos que te ayuden a comprender las implicaciones de estas tecnologías en términos de eficiencia y sostenibilidad en los negocios. Incrementar tu conocimiento sobre estos desarrollos te permitirá participar más activamente en discusiones estratégicas sobre cómo estas tecnologías pueden influir en tu organización.",
            5,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_2_70(self):
        """
        Test PDF text generation with question group 2 and score 70
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
            "Tu evaluación muestra un conocimiento básico de la línea de tiempo en la evolución tecnológica, pero hay espacio para mejorar tu comprensión y la conexión de los desarrollos científicos y de su impacto en los diferentes sectores. Identificas algunos de los avances clave; sin embargo, es importante que profundices más en cómo éstos han impactado en nuestras formas de trabajar, comunicarnos y consumir. Te sugiero que dediques tiempo a estudiar las aplicaciones actuales de la IA en diferentes industrias como logística, manufactura, de servicios entre otras, para visualizar cómo la tecnología redefine los modelos de negocio y las competencias necesarias. Y cómo las empresas están adoptando estas tecnologías para mejorar la toma de decisiones y optimizar los flujos de trabajo. Al ampliar tu comprensión sobre la automatización y el futuro del trabajo, podrás tener una visión más integral de la revolución digital y estar mejor preparado para tomar decisiones informadas y estratégicas.",
            5,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_2_100(self):
        """
        Test PDF text generation with question group 2 and score 100
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
            "Tu evaluación refleja un sólido conocimiento de la línea de tiempo en la evolución tecnológica y su impacto en la vida humana, lo que te posiciona bien para tomar decisiones estratégicas en un entorno altamente digitalizado. Para seguir avanzando, te sugiero que profundices en el impacto de la inteligencia artificial y la automatización en sectores específicos, como la atención médica, servicios y la manufactura o los que podrían aplicarse a tu organización. Estar al tanto de las últimas tendencias en IA te permitirá liderar la integración de estas tecnologías en tu organización para mejorar la productividad y la innovación. Además, sería beneficioso que investigaras más sobre las implicaciones éticas y sociales de la IA, especialmente en relación con la automatización del trabajo. De esta forma, podrás guiar a tu equipo y a tu organización hacia una adopción tecnológica sostenible, anticipando los desafíos del futuro del trabajo.",
            5,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_3_50(self):
        """
        Test PDF text generation with question group 3 and score 50
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
            "Tu evaluación indica que aún hay áreas importantes por desarrollar en cuanto a la comprensión de la diferencia entre Internet y la World Wide Web (WWW). Si bien es posible que tengas una noción general de ambas, es fundamental que profundices en cómo estas diferencias impactan directamente las decisiones estratégicas y la transformación digital. Los líderes que entienden que Internet no se limita solo a la WWW, sino que abarca una infraestructura más amplia, como la computación en la nube y la IoT (internet de las cosas), pueden identificar oportunidades más allá de las plataformas web para mejorar sus operaciones. Te recomiendo que inviertas tiempo en estudiar cómo la WWW se conecta con las interacciones con los clientes y cómo estas interacciones pueden mejorar a través de estrategias de marketing y comercio electrónico. Esto te permitirá desarrollar una perspectiva más completa sobre cómo aprovechar las tecnologías disponibles.",
            6,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_3_70(self):
        """
        Test PDF text generation with question group 3 and score 70
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
            "Tu evaluación muestra que tienes un buen entendimiento de la distinción entre Internet y la World Wide Web (WWW), pero hay oportunidades para mejorar en tu comprensión más detallada sobre cómo esta diferencia afecta la toma de decisiones estratégicas en el negocio. Reconoces que Internet es una infraestructura más amplia que permite la computación en la nube y la IoT (internet de las cosas), sin embargo, es importante que profundices más en cómo estos elementos impactan la transformación digital de los negocios, así podrás ser un aliado de los que lideran la tecnología en tú organización. Al integrar esta información con tu conocimiento sobre la WWW, podrás tomar decisiones más informadas sobre la seguridad cibernética y las inversiones tecnológicas. Considera también estudiar cómo estas distinciones influyen en la optimización de procesos internos y en la relación con los clientes para maximizar la eficiencia y la competitividad a largo plazo.",
            6,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_3_100(self):
        """
        Test PDF text generation with question group 3 and score 100
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
            "Tu evaluación refleja una sólida comprensión de la diferencia entre Internet y la World Wide Web (WWW), lo que te permite adoptar un enfoque estratégico más integral en la transformación digital y en las inversiones tecnológicas, súmate a los líderes que promueven este progreso. Tienes claro que la infraestructura de Internet va más allá de la WWW e incluye tecnologías como la computación en la nube, la IoT (internet de las cosas) y la cadena de bloques. Para seguir avanzando, te sugiero que continúes profundizando en el impacto de estas tecnologías emergentes, como la computación perimetral (edge computing) y la Internet industrial de las cosas (IIoT), que están remodelando el panorama digital. Al seguir desarrollando tu visión holística de cómo estas tecnologías interrelacionadas afectan la competitividad empresarial, podrás liderar de manera más efectiva la innovación, la protección de datos y las estrategias de crecimiento sostenible dentro de tu organización. ",
            6,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_4_50(self):
        """
        Test PDF text generation with question group 4 and score 50
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
            "Tu evaluación indica que aún necesitas mejorar significativamente en el uso y comprensión de los dispositivos digitales para maximizar tu productividad. En la actualidad, los líderes deben ser competentes en el uso de herramientas tecnológicas como teléfonos inteligentes, computadoras portátiles y tabletas para acceder a información clave en tiempo real, colaborar con equipos y gestionar tareas de manera eficiente. Si te resulta difícil conectar dispositivos en reuniones o manejar herramientas básicas como aplicaciones de análisis de datos o comunicación en la nube, es urgente que inviertas tiempo en familiarizarte con estas plataformas. Te recomiendo tomar cursos en línea o buscar mentoría para mejorar tu destreza en el uso de herramientas. También es importante que te acerques a la tecnología de automatización, como asistentes virtuales o aplicaciones de gestión de tareas, para optimizar tu tiempo y aumentar la eficiencia operativa. ",
            7,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_4_70(self):
        """
        Test PDF text generation with question group 4 and score 70
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
            "Tu evaluación muestra que tienes un conocimiento adecuado de cómo utilizar dispositivos digitales y sus aplicaciones para apoyar tu trabajo, pero hay áreas donde puedes mejorar para ser más eficiente y estratégico. Aunque eres capaz de manejar herramientas comunes para comunicarte, almacenar información o asistentes de IA básicos, es importante que profundices en cómo estas plataformas pueden integrarse más eficientemente en tu flujo de trabajo diario. Un área en la que podrías avanzar es en el uso de herramientas de análisis de datos, que te permitirán tomar decisiones informadas basadas en datos en tiempo real. Te sugiero que empieces a explorar este tipo de plataformas y que te enfoques en cómo pueden ayudarte a monitorear el desempeño y a realizar ajustes rápidos en las estrategias. Además, sería beneficioso que mejorases tus habilidades en la automatización de tareas repetitivas, utilizando aplicaciones de IA o sistemas de gestión de proyectos y equipos.",
            7,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_4_100(self):
        """
        Test PDF text generation with question group 4 and score 100
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
            "Tu evaluación refleja una sólida comprensión de los dispositivos digitales y sus aplicaciones, lo cual es una fortaleza clave en tu desempeño como líder. Seguramente utilizas herramientas de análisis de datos, colaboración en la nube y automatización de tareas de manera efectiva para optimizar tu tiempo y mejorar la productividad. Sin embargo, para continuar avanzando, te sugiero profundizar en el uso de aplicaciones avanzadas de IA, como asistentes virtuales personalizados o herramientas de análisis predictivo, que pueden ofrecerte nuevas formas de anticipar problemas y tomar decisiones más estratégicas. También es importante que compartas tus conocimientos con tu equipo, fomentando una cultura de adopción tecnológica y asegurándote de que todos estén alineados en el uso de estas herramientas. Esto fortalecerá aún más tu capacidad de liderazgo y tu impacto en la organización.",
            7,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_5_50(self):
        """
        Test PDF text generation with question group 5 and score 50
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
            "Tu evaluación sugiere que necesitas fortalecer tu comprensión de los aspectos clave de la ciberseguridad. Esta es un componente esencial en la vida empresarial, y es vital que comprendas los riesgos que enfrenta tu organización, como los ciberataques y las violaciones de datos. Asegúrate de familiarizarte y entender lo que tienes que hacer tú respecto a la protección de datos y la gestión de riesgos cibernéticos, ya que son fundamentales para proteger los activos digitales de la empresa. Te recomiendo invertir tiempo en formarte sobre las mejores prácticas de seguridad, incluyendo el cifrado de datos y la autenticación multifactor, y en mantenerte al tanto de las regulaciones de privacidad como el RGPD. Es crucial que trabajes en la integración de la ciberseguridad en todos los niveles de tu organización, ya que la falta de preparación en esta área puede llevar a consecuencias devastadoras, como pérdidas financieras y daños a la reputación.",
            8,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_5_70(self):
        """
        Test PDF text generation with question group 5 and score 70
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
            "Tu evaluación refleja que tienes una comprensión sólida de los principios básicos de ciberseguridad, pero aún hay espacio para mejorar en algunas áreas clave. Sabes cómo gestionar los riesgos y proteger los datos. Es recomendable que amplíes tu conocimiento en técnicas de defensa avanzadas, como el uso de la ingeniería social y el phishing, para entender cómo los atacantes provienen de explotar las debilidades humanas. Además, te sugiero que te enfoques en la creación de planes de respuesta a incidentes efectivos, de modo que tu organización pueda reaccionar rápidamente a cualquier brecha de seguridad. La educación continua en ciberseguridad es esencial, así que sería útil que participes en seminarios o cursos adicionales sobre los estándares de la industria, como el cumplimiento normativo con el RGPD. Con un esfuerzo adicional en estas áreas, podrás mejorar la capacidad de tu organización para responder a amenazas cibernéticas a tiempo.",
            8,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_5_100(self):
        """
        Test PDF text generation with question group 5 and score 100
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
            "Tu evaluación indica que tienes una comprensión avanzada de la ciberseguridad y de su impacto en la estrategia organizacional, lo que te posiciona como un líder capaz de tomar decisiones clave para proteger los activos digitales de la empresa. Dominas conceptos clave como la gestión de riesgos, la protección de datos y el cumplimiento normativo, y has integrado estas prácticas en las operaciones de la organización. Para seguir avanzando, te recomendaría que lideres iniciativas de concientización sobre ciberseguridad dentro de tu equipo y entorno laboral, asegurándote de que todos, desde los empleados hasta los altos ejecutivos, comprendan la importancia de una cultura de seguridad. También sería valioso que continúes evaluando y mejorando los planes de respuesta a incidentes de la empresa, apoya a los que lideran las áreas de tecnología en todo lo que soliciten, e impulsa las simulaciones regulares para asegurar una respuesta rápida ante cualquier brecha.",
            8,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_6_50(self):
        """
        Test PDF text generation with question group 6 and score 50
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
            "Tu evaluación indica que aún hay áreas críticas en las que es necesario mejorar tu comprensión y manejo de la huella digital. Como líder, debes entender que la huella digital que dejas a través de tus actividades en línea puede exponer a tu organización a riesgos de ciberseguridad significativos. Es urgente que empieces a adoptar prácticas básicas de protección, como usar contraseñas seguras, activar la autenticación multifactor y manejar de manera adecuada los datos confidenciales en la nube. Además, es fundamental que te familiarices con las políticas de privacidad de los servicios que utilizas y aprendas a reconocer los riesgos asociados con la ingeniería social y el phishing. Te sugiero que te capacites más en estas áreas mediante cursos y seminarios para evitar que tu huella digital quede desprotegida, lo que podría afectar tanto tu reputación como la seguridad de la organización.",
            9,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_6_70(self):
        """
        Test PDF text generation with question group 6 and score 70
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
            "Tu evaluación muestra que tienes una comprensión razonable de los conceptos básicos relacionados con la huella digital. Sin embargo, hay margen para profundizar y mejorar en áreas clave para fortalecer la protección de los activos digitales de la empresa. Si bien estás al tanto de la importancia de usar herramientas como VPNs y la autenticación multifactor, sería beneficioso que expandas tu conocimiento sobre la gestión de la huella digital en el uso de aplicaciones móviles y redes sociales. Es recomendable que ajustes regularmente las configuraciones de privacidad y accesos a archivos en la nube, y que empieces a realizar auditorías periódicas de tus cuentas en línea. Te sugiero también que refuerces tu educación en el uso de plataformas cifradas para proteger la información confidencial. Con una mayor atención a estos detalles, tu capacidad para gestionar los riesgos y proteger la organización será aún más sólida.",
            9,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_6_100(self):
        """
        Test PDF text generation with question group 6 and score 100
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
            "Tu evaluación refleja una comprensión avanzada sobre la huella digital, lo que te coloca en una posición fuerte como líder en la protección de los activos digitales de la organización. Dominas las estrategias clave, como el uso de contraseñas seguras, la encriptación de datos y la implementación de políticas de acceso controlado, lo cual es esencial para minimizar los riesgos. Para seguir avanzando, te sugiero que continúes investigando las últimas tendencias en ciberseguridad. Además, lidera iniciativas educativas dentro de la organización, capacitando a tu equipo sobre los riesgos de la huella digital y las mejores prácticas de seguridad. Fomentar una cultura de ciberseguridad contribuirá a fortalecer aún más la protección de la organización y minimizará las vulnerabilidades humanas. Mantente también al tanto de las regulaciones de privacidad y seguridad, asegurando que tu empresa cumpla con los estándares internacionales.",
            9,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_7_50(self):
        """
        Test PDF text generation with question group 7 and score 50
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
            "Tu evaluación indica que necesitas mejorar en varias áreas clave relacionadas con el uso responsable de la tecnología. Es esencial que empieces a comprender la importancia de ser un líder digital responsable, especialmente cuando se trata de proteger la privacidad, evitar el acoso cibernético y respetar la propiedad intelectual. Te recomiendo que comiences a reflexionar sobre cómo tu comportamiento digital puede influir en la cultura organizacional, desde las comunicaciones por correo electrónico hasta tu presencia en redes sociales. Es crucial que implementes prácticas éticas en tu uso de la tecnología, como ser transparente con tus interacciones digitales y garantizar que siempre das el crédito correspondiente a las ideas ajenas. Desarrollar estas competencias no solo te ayudará a liderar de manera más efectiva, sino que también contribuirá a un entorno digital más respetuoso y seguro dentro de la organización.",
            10,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_7_70(self):
        """
        Test PDF text generation with question group 7 and score 70
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
            "Tu evaluación muestra que tienes una comprensión adecuada de los principios del uso responsable de la tecnología, pero aún hay áreas en las que podrías profundizar para mejorar tu liderazgo digital. Sabes la importancia de evitar el plagio y proteger la privacidad, pero sería beneficioso que sigas desarrollando tu conocimiento sobre cómo crear un entorno digital respetuoso y ético. Te sugiero que te concentres en implementar prácticas más concretas para fomentar la ciudadanía digital dentro de tu equipo, como liderar talleres sobre los riesgos del acoso cibernético. Además, aunque eres consciente de la importancia de ser transparente en tu uso de la tecnología, es recomendable que sigas trabajando en tu capacidad para gestionar y comunicar las implicaciones éticas de nuevas tecnologías, como la inteligencia artificial, dentro de tu organización. Con una mayor concentración en estos temas, podrás fortalecer tu capacidad para guiar a tu equipo de manera responsable.",
            10,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_7_100(self):
        """
        Test PDF text generation with question group 7 and score 100
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
            "Tu evaluación refleja una comprensión avanzada y un enfoque ejemplar sobre el uso responsable de la tecnología. Estás bien posicionado para liderar con ética en el ámbito digital, lo que es fundamental para fomentar una cultura de integridad y respeto en tu organización. Has demostrado un compromiso con la transparencia, la privacidad y la creación de un ambiente digital seguro, lo cual es crucial para generar confianza tanto interna como externamente. Para seguir avanzando, te sugiero que sigas promoviendo la educación continua sobre el comportamiento ético en el uso de la tecnología dentro de tu equipo, asegurándote de que todos comprendan su responsabilidad digital. Además, sería valioso que lideres más iniciativas sobre los beneficios y riesgos de las tecnologías emergentes, como la IA y el análisis de datos, y cómo estas pueden implementarse de manera ética en la organización. ",
            10,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_8_50(self):
        """
        Test PDF text generation with question group 8 and score 50
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
            "Tu evaluación muestra que hay áreas clave en las que necesitas mejorar para ser más efectivo en el uso de herramientas de colaboración en línea. Es fundamental que te familiarices con las funciones básicas de plataformas más comunes que ahora están usando las organizaciones, ya que son herramientas esenciales para la comunicación y colaboración en equipos distribuidos. Sin una comprensión sólida de estas herramientas, podrías enfrentar dificultades al intentar gestionar equipos remotos o híbridos, lo que resultará en ineficiencias y decisiones más lentas. Te recomiendo que inviertas tiempo en capacitarte sobre las funcionalidades clave de estas plataformas, especialmente en áreas como el almacenamiento de archivos compartidos, la integración con otras aplicaciones y las capacidades de videoconferencia. A medida que te actualices en estas herramientas, mejorarás tanto la productividad como la eficiencia de tus equipos.",
            11,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_8_70(self):
        """
        Test PDF text generation with question group 8 and score 70
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
            "Tu evaluación indica que tienes un manejo adecuado de las herramientas de colaboración en línea, pero aún hay espacio para mejorar y profundizar en su utilización estratégica. Conoces las funciones básicas de herramientas más comunes que están usando las organizaciones, pero te sugiero que vayas más allá y explores las integraciones que pueden optimizar los flujos de trabajo dentro de tu organización. Integrar estas plataformas con otros sistemas, como CRM o herramientas de gestión de proyectos, te permitirá automatizar tareas repetitivas y mejorar la eficiencia operativa. También es importante que te familiarices con las capacidades de análisis de estas plataformas, que pueden brindarte información valiosa sobre el rendimiento del equipo y el progreso de los proyectos. Mejorar tus conocimientos en estas áreas no solo facilitará la gestión de equipos distribuidos, sino que también permitirá una mayor innovación y adaptabilidad a los modelos de trabajo híbridos.",
            11,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_8_100(self):
        """
        Test PDF text generation with question group 8 and score 100
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
            "Tu evaluación refleja una comprensión avanzada de las herramientas de colaboración en línea y su aplicación en un entorno de trabajo híbrido o remoto. Ya dominas las características clave de plataformas más comunes y eres capaz de utilizarlas para mejorar la eficiencia operativa y el rendimiento de tu equipo. Sin embargo, te sugiero que sigas explorando nuevas formas de integrar estas plataformas con otros sistemas de la organización, como CRM y ERP, para optimizar aún más los flujos de trabajo y automatizar tareas repetitivas. Te recomiendo que lideres la implementación de una estrategia de datos en tu organización. También sería beneficioso que continúes desarrollando tus habilidades en la gestión de equipos distribuidos, asegurando que el trabajo remoto e híbrido se gestione de manera eficiente y cohesionada. Siguiendo estos pasos, continuarás destacándote como un líder adaptado a las tendencias digitales y preparado para afrontar los retos futuros.",
            11,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_9_50(self):
        """
        Test PDF text generation with question group 9 and score 50
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
            "Tu evaluación indica que aún necesitas fortalecer tu comprensión sobre las tecnologías emergentes como la inteligencia artificial (IA), Realidad Virtual (RV), la cadena de bloques entre otros, que están transformando industrias y modelos de negocio. El hecho de no entender los aspectos clave de estas tecnologías podría limitar tu capacidad para liderar en un entorno digital en constante cambio. Te sugiero que empieces a familiarizarte con los diferentes tipos de IA, y cómo estas herramientas pueden aplicarse a tu área de trabajo. Asimismo, la comprensión de la cadena de bloques y sus aplicaciones prácticas, como la seguridad en las transacciones y los contratos inteligentes, te permitirá tomar decisiones más informadas. La falta de conocimiento en estas áreas también puede generar una desconexión con el equipo de TI y poner a la organización en desventaja frente a la competencia. ",
            12,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_9_70(self):
        """
        Test PDF text generation with question group 9 and score 70
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
            "Tu evaluación muestra que tienes una comprensión adecuada de las tecnologías emergentes, como la inteligencia artificial, Realidad Virtual (RV) y la cadena de bloques, pero aún hay áreas donde puedes mejorar para estar completamente al día con los avances en estas áreas. Tienes una base sólida, pero para optimizar el rendimiento de tu equipo y tomar decisiones más informadas, sería beneficioso profundizar más en la aplicación práctica de la IA en tu industria. Además, sería útil que profundices en la cadena de bloques y sus aplicaciones más allá de las criptomonedas, como los contratos inteligentes y la gestión de la cadena de suministro. Te sugiero que te centres en cómo estas tecnologías pueden integrarse mejor con los sistemas existentes en tu empresa y cómo su adopción puede mejorar la eficiencia operativa. Con un mayor enfoque en estas áreas, estarás mejor preparado para tomar decisiones estratégicas en un panorama tecnológico dinámico.",
            12,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_9_100(self):
        """
        Test PDF text generation with question group 9 and score 100
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
            "Tu evaluación refleja un sólido conocimiento y comprensión de las tecnologías emergentes, como la inteligencia artificial, Realidad Virtual (RV) y la cadena de bloques, lo que te coloca en una posición destacada, podrías ser líder digital fuera del área de tecnología. Dominas los conceptos clave y estás bien informado sobre cómo estas tecnologías pueden impactar tu industria y mejorar las operaciones. Para seguir avanzando, te sugiero que te enfoques en implementar la IA de manera más estratégica dentro de tu organización, para mejorar la productividad y la toma de decisiones. Además, dado tu conocimiento sobre la cadena de bloques, podrías explorar formas de integrar contratos inteligentes y otras aplicaciones descentralizadas para optimizar los procesos y aumentar la transparencia en las operaciones de la empresa. También sería valioso que lideres iniciativas educativas ayudando a tu equipo a comprender cómo estas tecnologías pueden mejorar su trabajo. ",
            12,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_10_50(self):
        """
        Test PDF text generation with question group 10 and score 50
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
            "Tu evaluación indica que aún hay áreas importantes en las que necesitas mejorar tu comprensión sobre las tecnologías de asistencia y su impacto en la inclusión y accesibilidad. Es fundamental que entiendas cómo estas tecnologías no solo mejoran la calidad de vida de las personas con capacidades diferentes, sino que también contribuyen a crear un entorno más equitativo. Te recomiendo que te enfoques en estudiar ejemplos clave, como los asistentes de voz, los lectores de pantalla y los dispositivos domésticos inteligentes, para comprender cómo funcionan y cómo pueden facilitar la vida cotidiana de las personas con diversas discapacidades. Además, es esencial que te mantengas informado sobre las últimas innovaciones en este campo, ya que la tecnología de asistencia está en constante evolución. La falta de conocimiento en esta área podría limitar tu capacidad para liderar iniciativas inclusivas en tu organización. ",
            13,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_10_70(self):
        """
        Test PDF text generation with question group 10 and score 70
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
            "Tu evaluación muestra que tienes una comprensión adecuada de las tecnologías de asistencia, pero aún puedes profundizar en su aplicación práctica y en su impacto directo en las personas con discapacidades. Estás al tanto de algunas de las herramientas clave, como los asistentes de voz y los lectores de pantalla, pero sería beneficioso si impulsas estos dispositivos dentro la organización. Te sugiero que te enfoques en comprender más a fondo los beneficios específicos de cada tecnología y cómo se pueden personalizar para satisfacer las necesidades individuales de las personas con capacidades diferentes. Además, explorar las implicaciones legales y sociales de estas tecnologías, como las normativas de accesibilidad digital y las políticas de inclusión, te permitirá comprender el panorama completo. Mejorar tu comprensión en estas áreas te permitirá ser un defensor más eficaz de la inclusión en tu organización y contribuir a un entorno más accesible y equitativo.",
            13,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_10_100(self):
        """
        Test PDF text generation with question group 10 and score 100
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
            "Tu evaluación refleja un conocimiento avanzado de las tecnologías de asistencia y su papel en la creación de una sociedad más inclusiva. Tienes una comprensión sólida de cómo estas herramientas, como los asistentes de voz, los lectores de pantalla y los dispositivos domésticos inteligentes, benefician a las personas con capacidades diferentes, facilitando su independencia y participación en la sociedad. Para seguir avanzando, te sugiero que tomes un enfoque proactivo en la implementación de estas tecnologías dentro de tu organización, garantizando que todos los empleados, independientemente de sus capacidades, tengan acceso a herramientas que mejoren su productividad y bienestar. Además, sería beneficioso que lideres iniciativas para aumentar la conciencia sobre la importancia de la accesibilidad digital y cómo se pueden integrar soluciones de tecnología de asistencia en la vida cotidiana de manera efectiva. ",
            13,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_11_50(self):
        """
        Test PDF text generation with question group 11 and score 50
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
            'Tu evaluación sugiere que aún no has integrado completamente las consideraciones necesarias sobre el uso de las redes sociales. En la era digital, las redes sociales son una herramienta poderosa tanto en lo personal como en lo profesional, y un mal manejo de ellas puede afectar negativamente tanto tu reputación como la de la organización que lideras. El uso de estas puede impactar en la confianza de tus colaboradores, tu influencia como líder y la productividad de tu equipo. Te recomiendo que tomes medidas inmediatas para ajustar tu comportamiento en redes sociales, estableciendo límites claros sobre tu tiempo de uso y mejorando tus configuraciones de privacidad. Además, considera las recomendaciones sobre "desintoxicación digital" para equilibrar mejor tu bienestar y productividad. A medida que tomes control de tu presencia digital, serás capaz de modelar un comportamiento positivo para tu equipo y mejorar la imagen de la empresa.',
            14,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_11_70(self):
        """
        Test PDF text generation with question group 11 and score 70
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
            "Tu evaluación muestra que tienes una comprensión razonable sobre el impacto que el uso de redes sociales puede tener en tu liderazgo y en los resultados de negocio. Eres consciente de la importancia de la reputación personal y profesional, así como de la influencia que ejerces en tu equipo y en las relaciones con clientes. Sin embargo, para optimizar tu presencia digital y mejorar el bienestar en línea, te sugiero que implementes cambios prácticos como el establecimiento de límites de tiempo para el uso de redes sociales. Además, sería beneficioso que reflexionaras más sobre las implicaciones a largo plazo de lo que compartes y cómo esto puede afectar la percepción pública de tu marca personal y la empresa. Practicar descansos periódicos de las redes sociales y educarte más sobre la gestión del acoso cibernético te permitirá fomentar un entorno de trabajo más saludable, a la vez que proteges tu bienestar y el de tu equipo. ",
            14,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_11_100(self):
        """
        Test PDF text generation with question group 11 and score 100
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
            "Tu evaluación refleja una comprensión avanzada de los desafíos y oportunidades que presentan las redes sociales para los líderes en la era digital. Tus respuestas sugieren que manejas bien tu presencia en línea, lo que te permite influir positivamente en tu equipo, mejorar la percepción pública de la empresa y generar relaciones de confianza con clientes y socios. No obstante, te recomiendo que sigas perfeccionando tu enfoque al establecer límites aún más rigurosos en el tiempo que dedicas a las redes sociales, para que puedas concentrarte en las prioridades profesionales y reducir la presión psicológica de la conectividad constante. Además, dado tu conocimiento, sería valioso que lideres iniciativas dentro de tu organización para educar a tu equipo sobre el uso responsable de las plataformas digitales, promoviendo una cultura de bienestar y respeto en línea. Siguiendo estas prácticas, fortalecerás tu influencia como un líder responsable y equilibrado.",
            14,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_12_50(self):
        """
        Test PDF text generation with question group 12 and score 50
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
            "Tu evaluación indica que aún necesitas mejorar tu comprensión sobre cómo la tecnología puede impactar el medio ambiente y cómo las prácticas sostenibles pueden mitigar estos efectos. Te recomiendo que empieces a estudiar las prácticas recomendadas para reducir el impacto ambiental, como el uso de dispositivos de bajo consumo de energía y el reciclaje de aparatos electrónicos. Además, es fundamental que aprendas cómo la adopción de energías renovables y la optimización del consumo de recursos tecnológicos pueden ayudar a minimizar la huella de carbono de tu organización. La falta de conocimiento sobre estos temas podría resultar en decisiones poco informadas que afecten tanto a la sostenibilidad ambiental como a los resultados comerciales. Invierte tiempo en investigar tecnologías ecológicas y cómo éstas pueden ser implementadas de manera efectiva en tu empresa. Plantéate la necesidad de ser un aliado para quien lidera la tecnología en la organización.",
            15,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_12_70(self):
        """
        Test PDF text generation with question group 12 and score 70
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
            "Tu evaluación muestra que tienes un conocimiento adecuado sobre la relación entre la tecnología y el medio ambiente, pero aún hay áreas donde podrías profundizar para estar completamente alineado con las mejores prácticas sostenibles. Eres consciente de la importancia de adoptar hábitos como la reducción del uso de papel y el reciclaje de aparatos electrónicos, pero te sugeriría que explores más ejemplos de tecnologías ecológicas y cómo estas pueden contribuir a la sostenibilidad a nivel organizacional. Considera implementar prácticas adicionales, como la adopción de energías renovables en tus operaciones o la promoción de dispositivos de bajo consumo de energía dentro de tu empresa. Además, sería valioso que educaras a tu equipo sobre la importancia de la gestión de desechos electrónicos y las implicaciones de no adoptar políticas de sostenibilidad. Al fortalecer estos aspectos, fomentarás una cultura organizacional consciente del medio ambiente.",
            15,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_12_100(self):
        """
        Test PDF text generation with question group 12 and score 100
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
            "Tu evaluación refleja un excelente dominio de las prácticas sostenibles relacionadas con la tecnología y el medio ambiente. Tienes una comprensión profunda de cómo la adopción de tecnologías ecológicas, como el uso de energías renovables y el reciclaje de equipos electrónicos, pueden beneficiar tanto al medio ambiente como a la sostenibilidad de la empresa. Te sugiero que tomes la iniciativa para liderar dentro de tu organización, implementando políticas más rigurosas que promuevan la eficiencia energética y la reducción de la huella de carbono. Además, puedes considerar la creación de una estrategia de sostenibilidad más robusta que incluya la optimización de recursos tecnológicos y la integración de soluciones más verdes en todos los aspectos de la operación empresarial. Sigue explorando nuevas tecnologías ecológicas y asegúrate de que tu empresa esté a la vanguardia en cuanto a sostenibilidad digital.",
            15,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_13_50(self):
        """
        Test PDF text generation with question group 13 and score 50
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
            "Tu evaluación sugiere que es necesario mejorar en varios aspectos clave relacionados con la etiqueta digital. El respeto y la claridad en la comunicación en línea son esenciales para un liderazgo efectivo en el entorno digital, y parece que aún no has integrado completamente estos principios en tus interacciones. Te recomiendo que trabajes en desarrollar una comunicación respetuosa y profesional en todas las plataformas digitales, ya sea en correos electrónicos, chats o videollamadas. También es importante que establezcas expectativas claras sobre los tiempos de respuesta y seas consciente del tono que utilizas, evitando el sarcasmo y la ambigüedad. Además, es fundamental que consideres las diferencias generacionales en la forma de comunicarte. Comprender y aplicar estos principios no solo fortalecerá tu liderazgo, sino que también contribuirá a crear un ambiente más productivo y respetuoso para tu equipo. ",
            16,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_13_70(self):
        """
        Test PDF text generation with question group 13 and score 70
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
            "Tu evaluación muestra que tienes una comprensión razonable de la etiqueta digital, pero hay oportunidades para profundizar y mejorar aún más. Sabes la importancia de mantener una comunicación respetuosa y de responder de manera clara y oportuna; sin embargo, en algunas ocasiones podría ser útil que ajustes tu enfoque según la plataforma o la generación con la que estés interactuando. Te recomiendo que refuerces tu capacidad para gestionar la comunicación multicanal, adaptándola al contexto y a la audiencia. Además, es crucial que seas más consciente del impacto de tu lenguaje en la interacción, priorizando un tono respetuoso e inclusivo, independientemente de si estás interactuando con compañeros más jóvenes o mayores. Otro aspecto que podrías mejorar es el respeto por los límites digitales, especialmente en un entorno remoto, asegurándote de no sobrecargar a tu equipo fuera del horario laboral.",
            16,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_with_question_group_13_100(self):
        """
        Test PDF text generation with question group 13 and score 100
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
            "Tu evaluación refleja un nivel sobresaliente en cuanto a etiqueta digital, lo que indica que tienes una gran capacidad para comunicarte de manera respetuosa y profesional en plataformas digitales. Sabes manejar diferentes tipos de comunicación y eres consciente de la importancia de la rapidez y la claridad en las respuestas. Además, muestras una excelente habilidad para adaptarte a las expectativas de las diversas generaciones, lo que te permite gestionar equipos de manera efectiva en un entorno digital. Sin embargo, es importante que continúes perfeccionando tu capacidad para respetar los límites digitales, tanto para ti como para tu equipo, especialmente en un entorno remoto donde el trabajo puede fácilmente invadir el tiempo personal. Te sugiero que sigas promoviendo un uso responsable de las tecnologías y sigas modelando un comportamiento digital positivo para tu equipo. No olvides que liderar con el ejemplo es una ventaja única. ",
            16,
        )

        self.assertTrue(text_in_pdf)


class GenerateNextReportTextPDFSummaryTestCase(GenerateNextReportBase):
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

    def test_generate_pdf_summary_CD_with_100(self):
        """
        Test PDF summary text generation with score 100
        """

        selected_options = self.__get_selected_options(score=100)
        self.create_report(
            options=selected_options, invitation_code=self.invitation_code
        )

        # create and get pdf
        pdf_path = self.create_get_pdf()

        # Validate text in pdf
        text_in_pdf = self.validate_text_in_pdf(
            pdf_path,
            "Líder promotor de la cultura digital",
            19,
        )

        self.assertTrue(text_in_pdf)

        text_in_pdf = self.validate_text_in_pdf(
            pdf_path,
            "Demuestra seguridad en el uso de herramientas digitales, participa activamente en conversaciones sobre tecnología, integra soluciones innovadoras en su gestión diaria y promueve un entorno digital ético, inclusivo y sostenible. Es percibido como un líder actualizado y abierto al cambio.",
            19,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_summary_CD_with_80(self):
        """
        Test PDF summary text generation with score 80
        """

        selected_options = self.__get_selected_options(score=79)
        self.create_report(
            options=selected_options, invitation_code=self.invitation_code
        )

        # create and get pdf
        pdf_path = self.create_get_pdf()

        # Validate text in pdf
        text_in_pdf = self.validate_text_in_pdf(
            pdf_path,
            "Líder en adaptación digital",
            19,
        )

        self.assertTrue(text_in_pdf)

        text_in_pdf = self.validate_text_in_pdf(
            pdf_path,
            "Ha comenzado a incorporar herramientas y conceptos digitales en su práctica diaria, aunque aún depende de apoyo para aplicarlos de forma estratégica. Muestra disposición al aprendizaje, pero necesita mayor consistencia para liderar con seguridad en entornos digitales. Podría hacer un mayor esfuerzo para convertirse en un aliado del área de tecnología en esta era digital.",
            19,
        )

        self.assertTrue(text_in_pdf)

    def test_generate_pdf_summary_CD_with_50(self):
        """
        Test PDF summary text generation with score 50
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
            "Líder alejado de la cultura digital",
            19,
        )

        self.assertTrue(text_in_pdf)

        text_in_pdf = self.validate_text_in_pdf(
            pdf_path,
            "Evita o delega de forma constante los temas relacionados con tecnología, muestra dificultad para adaptarse a entornos digitales y rara vez incorpora soluciones tecnológicas en su práctica diaria. Su liderazgo no refleja una comprensión clara del entorno digital actual. Podría hacer un mayor esfuerzo para convertirse en un aliado del área de tecnología en esta era digital.",
            19,
        )

        self.assertTrue(text_in_pdf)
