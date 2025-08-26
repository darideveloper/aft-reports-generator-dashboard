from bs4 import BeautifulSoup

from core.tests_base.test_admin import TestAdminBase
from core.tests_base.test_models import TestSurveyModelBase


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

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)

    def test_custom_links(self):
        """Validate custom links working"""

        # Create required data
        survey = self.create_survey()
        participant = self.create_participant()
        report = self.create_report(survey=survey, participant=participant)

        # Validate response
        response = self.client.get(f"{self.endpoint}")
        self.assertEqual(response.status_code, 200)

        # Validate link "Ver Reporte" to /report/1/
        soup = BeautifulSoup(response.content, "html.parser")
        link = soup.select_one("#result_list a.btn-primary")
        self.assertIsNotNone(link)
        self.assertEqual(link["href"], f"/report/{report.id}/")
