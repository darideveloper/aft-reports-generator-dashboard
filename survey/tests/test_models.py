from core.tests_base.test_models import TestSurveyModelBase


class ReportTestCase(TestSurveyModelBase):
    """Testing report model"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/survey/report/"

    def test_save_single_report(self):
        """Validate save single report"""
        report = self.create_report()
        
        # Set total to report
        report.total = 100
        report.save()

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
        
        # Set total to each report
        report_1.total = 100
        report_2.total = 100
        report_3.total = 100
        report_1.save()
        report_2.save()
        report_3.save()

        average = report_1.total + report_2.total + report_3.total
        average = average / 3

        self.assertEqual(average, company.average_total)

    def test_save_many_report_multi_company(self):
        """Validate save many reports for multi company"""
        company_1 = self.create_company()
        company_2 = self.create_company()
        
        participant_1 = self.create_participant(company=company_1)
        participant_2 = self.create_participant(company=company_1)
        participant_3 = self.create_participant(company=company_2)
        participant_4 = self.create_participant(company=company_2)

        report_1 = self.create_report(participant=participant_1)
        report_2 = self.create_report(participant=participant_2)
        report_3 = self.create_report(participant=participant_3)
        report_4 = self.create_report(participant=participant_4)
        
        # Set total to each report
        report_1.total = 100
        report_2.total = 100
        report_3.total = 100
        report_4.total = 100
        report_1.save()
        report_2.save()
        report_3.save()
        report_4.save()

        average_1 = report_1.total + report_2.total
        average_1 = average_1 / 2

        average_2 = report_3.total + report_4.total
        average_2 = average_2 / 2

        self.assertEqual(average_1, company_1.average_total)
        self.assertEqual(average_2, company_2.average_total)


        

        
        
