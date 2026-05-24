from unittest import mock
from django.conf import settings
from django.core.management import call_command
from core.tests_base.test_models import TestSurveyModelBase
from survey import models as survey_models


class ReportsDownloadModelTestCase(TestSurveyModelBase):

    @mock.patch("survey.models.requests.get")
    def test_save_triggers_api_call(self, mock_get):
        # Configure the mock to return a 200 status code
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Success"}
        mock_get.return_value = mock_response

        # Create a new ReportsDownload instance using helper
        download = self.create_reports_download()
        download.trigger_webhook()

        # Check if api call was made
        expected_url = f"{settings.N8N_BASE_WEBHOOKS}/aft-create-reports-download-file"
        mock_get.assert_called_once_with(expected_url)

        # Verify status update based on response
        self.assertEqual(download.status, "pending")

    @mock.patch("survey.models.requests.get")
    def test_save_api_call_failure(self, mock_get):
        # Configure the mock to return a non-200 status code
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Failed"}
        mock_get.return_value = mock_response

        # Create a new ReportsDownload instance using helper
        download = self.create_reports_download()
        download.trigger_webhook()

        # Check if api call was made
        expected_url = f"{settings.N8N_BASE_WEBHOOKS}/aft-create-reports-download-file"
        mock_get.assert_called_once_with(expected_url)

        # Verify status update based on response
        self.assertEqual(download.status, "error")



class ReportSummaryScoreModelTestCase(TestSurveyModelBase):
    def test_report_summary_score_creation(self):
        from django.contrib.auth.models import User
        # Need to load initial data for create_report to work (it depends on survey ID=1)
        call_command("apps_loaddata")
        call_command("initial_loaddata")

        # Create superuser and login
        username = "test_user"
        password = "test_pass"
        User.objects.create_superuser(
            username=username,
            email="test@gmail.com",
            password=password,
        )
        self.client.login(username=username, password=password)

        self.company = self.create_company()

        report = self.create_report()
        
        # Verify that summary scores were created automatically by the serializer
        summary_scores = survey_models.ReportSummaryScore.objects.filter(report=report)
        self.assertTrue(summary_scores.exists())
        
        # Check specific category
        cd_score = summary_scores.filter(paragraph_type="CD").first()
        self.assertIsNotNone(cd_score)
        # In a fresh test with no answers, score might be 0 or fallback to report.total
        self.assertEqual(cd_score.score, report.total)


class GroupReportModelTestCase(TestSurveyModelBase):

    @mock.patch("survey.models.requests.get")
    def test_save_triggers_webhook(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Success"}
        mock_get.return_value = mock_response

        group_report = self.create_group_report()
        group_report.trigger_webhook()

        expected_url = f"{settings.N8N_BASE_WEBHOOKS}/aft-create-group-report-file"
        mock_get.assert_called_once_with(expected_url)
        self.assertEqual(group_report.status, "pending")

    @mock.patch("survey.models.requests.get")
    def test_save_webhook_failure(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Failed"}
        mock_get.return_value = mock_response

        group_report = self.create_group_report()
        group_report.trigger_webhook()

        expected_url = f"{settings.N8N_BASE_WEBHOOKS}/aft-create-group-report-file"
        mock_get.assert_called_once_with(expected_url)
        self.assertEqual(group_report.status, "error")
        self.assertIn("Failed", group_report.logs)


    @mock.patch("survey.models.requests.get")
    def test_generate_group_report_pdf(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Success"}
        mock_get.return_value = mock_response

        from django.contrib.auth.models import User
        call_command("apps_loaddata")
        call_command("initial_loaddata")

        username = "test_user"
        password = "test_pass"
        User.objects.create_superuser(
            username=username,
            email="test@gmail.com",
            password=password,
        )
        self.client.login(username=username, password=password)

        self.company = self.create_company()
        report = self.create_report()

        from utils.group_report_generator import generate_group_report_pdf

        reports = survey_models.Report.objects.filter(id=report.id)
        pdf_bytes = generate_group_report_pdf(
            reports=reports,
            company_name=self.company.name,
        )
        self.assertIsNotNone(pdf_bytes)
        self.assertGreater(len(pdf_bytes), 0)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    @mock.patch("survey.models.requests.get")
    def test_admin_action_creates_group_report(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Success"}
        mock_get.return_value = mock_response

        from django.contrib.auth.models import User
        call_command("apps_loaddata")
        call_command("initial_loaddata")

        username = "test_user"
        password = "test_pass"
        User.objects.create_superuser(
            username=username,
            email="test@gmail.com",
            password=password,
        )
        self.client.login(username=username, password=password)

        self.company = self.create_company()
        report = self.create_report()

        response = self.client.post(
            "/admin/survey/report/",
            {
                "action": "create_group_report",
                "_selected_action": [report.id],
            },
        )
        self.assertEqual(response.status_code, 302)

        group_report = survey_models.GroupReport.objects.first()
        self.assertIsNotNone(group_report)
        self.assertIn(report, group_report.reports.all())

    @mock.patch("survey.models.requests.get")
    def test_management_command_processes_pending(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Success"}
        mock_get.return_value = mock_response

        from django.contrib.auth.models import User
        call_command("apps_loaddata")
        call_command("initial_loaddata")

        username = "test_user"
        password = "test_pass"
        User.objects.create_superuser(
            username=username,
            email="test@gmail.com",
            password=password,
        )
        self.client.login(username=username, password=password)

        self.company = self.create_company()
        report = self.create_report()
        report.status = "completed"
        report.save()

        group_report = self.create_group_report(
            reports=[report],
            company=self.company,
        )

        call_command("create_group_report")

        group_report.refresh_from_db()
        self.assertEqual(group_report.status, "completed")
        self.assertTrue(group_report.pdf_file)

    @mock.patch("survey.models.requests.get")
    def test_route_admin_only(self, mock_get):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Success"}
        mock_get.return_value = mock_response

        from django.contrib.auth.models import User
        call_command("apps_loaddata")
        call_command("initial_loaddata")

        self.company = self.create_company()

        response = self.client.get(f"/group-report-pdf/{self.company.id}/")
        self.assertEqual(response.status_code, 302)

        username = "test_user"
        password = "test_pass"
        User.objects.create_superuser(
            username=username,
            email="test@gmail.com",
            password=password,
        )
        self.client.login(username=username, password=password)

        response = self.client.get(f"/group-report-pdf/{self.company.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")


class TextPDFSummaryModelTestCase(TestSurveyModelBase):
    def test_text_pdf_summary_mapping(self):
        call_command("apps_loaddata")
        call_command("initial_loaddata")

        qg1 = survey_models.QuestionGroup.objects.get(survey_index=1)
        qg2 = survey_models.QuestionGroup.objects.get(survey_index=2)

        summary = self.create_text_pdf_summary(
            paragraph_type="CD", question_groups=[qg1, qg2]
        )

        self.assertEqual(summary.question_groups.count(), 2)
        self.assertIn(qg1, summary.question_groups.all())
        self.assertIn(qg2, summary.question_groups.all())
