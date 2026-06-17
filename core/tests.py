from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.test import override_settings
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase

class SMTPValidationEndpointTests(APITestCase):
    def setUp(self):
        self.url = reverse("validate-email")
        self.valid_token = "test_token_123"

    @override_settings(SMTP_TEST_TOKEN=None)
    def test_missing_expected_token(self):
        # If SMTP_TEST_TOKEN settings is None, return 500
        response = self.client.post(self.url, {"token": self.valid_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["status"], "error")
        self.assertIn("not configured", response.data["message"])

    @override_settings(SMTP_TEST_TOKEN="test_token_123")
    def test_invalid_token(self):
        # Missing token parameter
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["status"], "error")

        # Invalid token value
        response = self.client.post(self.url, {"token": "wrong_token"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["status"], "error")

    @override_settings(SMTP_TEST_TOKEN="test_token_123")
    @patch("core.views.get_connection")
    def test_emulated_success(self, mock_get_connection):
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection

        response = self.client.post(self.url, {"token": self.valid_token}, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertTrue(response.data["emulated"])
        
        # Verify connection was opened and closed
        mock_connection.open.assert_called_once()
        mock_connection.close.assert_called_once()

    @override_settings(SMTP_TEST_TOKEN="test_token_123")
    def test_real_send_missing_email(self):
        response = self.client.post(self.url, {"token": self.valid_token, "real": True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")
        self.assertIn("email", response.data["message"])

    @override_settings(SMTP_TEST_TOKEN="test_token_123")
    @patch("core.views.get_connection")
    def test_real_send_success(self, mock_get_connection):
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection

        # Reset mail outbox
        mail.outbox = []

        response = self.client.post(
            self.url, 
            {"token": self.valid_token, "real": True, "email": "test@example.com"},
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertFalse(response.data["emulated"])
        
        # Verify connection open/close
        mock_connection.open.assert_called_once()
        mock_connection.close.assert_called_once()

    @override_settings(SMTP_TEST_TOKEN="test_token_123")
    @patch("core.views.get_connection")
    def test_smtp_connection_failure(self, mock_get_connection):
        mock_connection = MagicMock()
        # Mock connection open to raise an SMTP or connection exception
        mock_connection.open.side_effect = Exception("Connection timed out")
        mock_get_connection.return_value = mock_connection

        response = self.client.post(self.url, {"token": self.valid_token}, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["status"], "error")
        self.assertIn("Connection timed out", response.data["message"])

    @override_settings(SMTP_TEST_TOKEN="test_token_123")
    def test_invalid_json_payload(self):
        # Sending malformed/raw content that is not valid JSON
        response = self.client.post(
            self.url,
            data="not-a-json-string",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")
        self.assertIn("Invalid JSON", response.data["message"])

