from django.test import TestCase
from django.urls import reverse
from django.core import mail
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Event, Lead


class EventModelTestCase(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title="Conferencia de Pruebas",
            slug="test-conference",
            notify_email="organizer@example.com",
            name_active=True,
            name_required=True,
            company_active=False,
            company_required=False,
        )

    def test_event_creation(self):
        self.assertEqual(self.event.title, "Conferencia de Pruebas")
        self.assertEqual(self.event.slug, "test-conference")
        self.assertEqual(str(self.event), "Conferencia de Pruebas")


class LeadSubmitAPITestCase(APITestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title="Conferencia de Tecnología",
            slug="tech-conf-2026",
            notify_email="admin@example.com",
            # Fields configuration
            name_active=True,
            name_required=True,
            position_active=True,
            position_required=False,
            email_active=True,
            email_required=True,
            phone_active=False,
            phone_required=False,
            company_active=False,
            company_required=False,
        )
        self.submit_url = reverse("lead-submit", kwargs={"slug": self.event.slug})

    def test_successful_lead_submission(self):
        data = {
            "name": "Juan Perez",
            "email": "juan@example.com",
            "job_position": "Desarrollador",
            "phone": "555-1234",  # Inactive field, will be ignored
            "website": "",  # Empty honeypot
        }

        response = self.client.post(self.submit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "ok")

        # Verify Lead creation in database
        lead = Lead.objects.get(event=self.event)
        self.assertEqual(lead.name, "Juan Perez")
        self.assertEqual(lead.email, "juan@example.com")
        self.assertEqual(lead.job_position, "Desarrollador")
        self.assertIsNone(lead.phone)  # Inactive field must be set to None
        self.assertFalse(lead.is_spam)

        # Verify emails dispatched
        self.assertEqual(len(mail.outbox), 2)  # One for admin, one for client
        self.assertEqual(mail.outbox[0].subject, f"Nuevo registro: {self.event.title}")
        self.assertEqual(mail.outbox[1].subject, f"Confirmación de registro: {self.event.title}")

    def test_missing_required_field_returns_400(self):
        data = {
            "name": "",  # Required name is empty
            "email": "juan@example.com",
            "website": "",
        }

        response = self.client.post(self.submit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data["errors"])
        self.assertEqual(
            response.data["errors"]["name"][0],
            "El campo nombre es requerido.",
        )

        # Ensure no lead was saved and no email sent
        self.assertFalse(Lead.objects.filter(event=self.event).exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_honeypot_silently_flags_spam(self):
        data = {
            "name": "Spam Bot",
            "email": "bot@spam.com",
            "website": "http://spam-link.com",  # Honeypot filled!
        }

        response = self.client.post(self.submit_url, data, format="json")
        # Returns simulated success (201 Created) to trick the bot
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "ok")

        # Verify Lead is created in DB but marked as spam
        lead = Lead.objects.get(event=self.event)
        self.assertEqual(lead.name, "Spam Bot")
        self.assertTrue(lead.is_spam)

        # Verify NO emails were sent
        self.assertEqual(len(mail.outbox), 0)

    @patch("django.core.mail.EmailMultiAlternatives.send")
    def test_database_save_succeeds_on_smtp_error(self, mock_send):
        # Mock SMTP connection failure
        mock_send.side_effect = Exception("SMTP Connection Refused")

        data = {
            "name": "Maria Lopez",
            "email": "maria@example.com",
            "website": "",
        }

        response = self.client.post(self.submit_url, data, format="json")
        # API must return success status, preserving database records
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify data is still stored safely
        self.assertTrue(Lead.objects.filter(event=self.event, name="Maria Lopez").exists())

    def test_event_form_branding_rendering(self):
        url = reverse("events:event-form", kwargs={"slug": self.event.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify context contains branding settings
        self.assertIn("branding", response.context)
        self.assertEqual(response.context["branding"]["colors"]["primary"], "#0a3c58")

        # Verify template HTML rendering contains brand assets and colors
        content = response.content.decode("utf-8")
        self.assertIn("#0a3c58", content)
        self.assertIn("#072a3e", content)
        self.assertIn("https://aft-reports-generator.s3.amazonaws.com/static/core/imgs/logo-leadforward.jpg", content)

    def test_confirmation_email_branding_and_signature(self):
        data = {
            "name": "Alex Smith",
            "email": "alex@example.com",
            "website": "",
        }
        response = self.client.post(self.submit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify client email formatting and signature
        self.assertEqual(len(mail.outbox), 2)
        client_mail = mail.outbox[1]
        self.assertEqual(client_mail.subject, f"Confirmación de registro: {self.event.title}")

        # Text version checks
        self.assertIn("El equipo LeadForward Global Solutions MJ", client_mail.body)

        # HTML version checks
        html_content = client_mail.alternatives[0][0]
        self.assertIn("#0a3c58", html_content)
        self.assertIn("El equipo LeadForward Global Solutions MJ", html_content)
        self.assertIn("https://aft-reports-generator.s3.amazonaws.com/static/core/imgs/logo-leadforward.jpg", html_content)

