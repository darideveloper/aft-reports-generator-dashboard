from core.tests_base.test_models import TestSurveyModelBase


class ReportTestCase(TestSurveyModelBase):
    """Testing report model"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/report/"
    
    
    