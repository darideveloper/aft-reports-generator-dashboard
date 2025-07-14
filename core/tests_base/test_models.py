from django.test import TestCase

from survey import models as survey_models


class TestSurveyModelBase(TestCase):
    """Test survey models"""

    def create_company(
        self,
        name: str = "Company test",
        details: str = "Test description",
        logo: str = "test.webp",
        invitation_code: str = "test",
        is_active: bool = True,
    ) -> survey_models.Company:
        """Create a company object"""

        return survey_models.Company.objects.create(
            name=name,
            details=details,
            logo=logo,
            invitation_code=invitation_code,
            is_active=is_active,
        )
