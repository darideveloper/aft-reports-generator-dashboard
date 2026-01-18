from unittest import mock
from django.conf import settings
from core.tests_base.test_models import TestSurveyModelBase


class ReportsDownloadModelTestCase(TestSurveyModelBase):

    @mock.patch("survey.models.requests.get")
    def test_save_triggers_api_call(self, mock_get):
        # Configure the mock to return a 200 status code
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Success"}
        mock_get.return_value = mock_response

        # Create a new ReportsDownload instance using helper
        # This calls save() which should trigger the API call
        download = self.create_reports_download()

        # Check if api call was made
        expected_url = f"{settings.N8N_BASE_WEBHOOKS}/aft-create-reports-download-file"
        mock_get.assert_called_once_with(expected_url)

        # Verify status update based on response
        self.assertEqual(download.status, "processing")

    @mock.patch("survey.models.requests.get")
    def test_save_api_call_failure(self, mock_get):
        # Configure the mock to return a non-200 status code
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Failed"}
        mock_get.return_value = mock_response

        # Create a new ReportsDownload instance using helper
        download = self.create_reports_download()

        # Check if api call was made
        expected_url = f"{settings.N8N_BASE_WEBHOOKS}/aft-create-reports-download-file"
        mock_get.assert_called_once_with(expected_url)

        # Verify status update based on response
        self.assertEqual(download.status, "error")
