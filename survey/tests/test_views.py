from rest_framework import status

from core.tests_base.test_views import TestSurveyViewsBase

from survey import models as survey_models


class InvitationCodeViewTestCase(TestSurveyViewsBase):

    def setUp(self):
        # Set endpoint
        super().setUp(
            endpoint="/api/invitation-code/", restricted_post=False, restricted_get=True
        )

    def test_post_valid_invitation_code(self):
        """Test post request with valid invitation code"""
        payload = {"invitation_code": "test"}

        response = self.client.post(self.endpoint, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("ok", response.data["status"])

    def test_post_invalid_invitation_code(self):
        """Test post request with invalid invitation code"""
        payload = {"invitation_code": "invalid_code"}

        response = self.client.post(self.endpoint, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data["status"])

    def test_post_invitation_code_no_companies(self):
        """Test post request with no companies in the database"""
        # Delete all companies
        survey_models.Company.objects.all().delete()

        payload = {"invitation_code": "test"}

        response = self.client.post(self.endpoint, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data["status"])

    def test_post_valid_invitation_code_inactive_company(self):
        """Test post request with valid invitation code but inactive company"""
        payload = {"invitation_code": "test"}

        self.company_1.is_active = False
        self.company_1.save()

        response = self.client.post(self.endpoint, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data["status"])
