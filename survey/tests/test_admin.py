from core.tests_base.test_admin import TestAdminBase


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


class QuestionOptionAdminTestCase(TestAdminBase):
    """Testing question option admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/questionoption/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class ParticipantAdminTestCase(TestAdminBase):
    """Testing participant admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/participant/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class AnswerAdminTestCase(TestAdminBase):
    """Testing answer admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/answer/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)
