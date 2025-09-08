from core.tests_base.test_models import TestSurveyModelBase


class ReportTestCase(TestSurveyModelBase):
    """Testing report model"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/report/"

    def test_save_single_report(self):
        """Validate save single report"""
        report = self.create_report()

        company = report.participant.company

        self.assertEqual(report.total, company.average_total)
        
