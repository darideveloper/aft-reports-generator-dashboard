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

    def test_save_many_reports_single_company(self):
        """Validate save many reports for single company"""
        company = self.create_company()

        participant_1 = self.create_participant(company=company)
        participant_2 = self.create_participant(company=company)
        participant_3 = self.create_participant(company=company)

        report_1 = self.create_report(participant=participant_1)
        report_2 = self.create_report(participant=participant_2)
        report_3 = self.create_report(participant=participant_3)

        average = report_1.total + report_2.total + report_3.total
        average = average / 3

        self.assertEqual(average, company.average_total)

        
        
