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

    def create_survey(
        self,
        name: str = "Survey test",
        instructions: str = "Test instructions",
    ) -> survey_models.Survey:
        """Create a survey object"""

        return survey_models.Survey.objects.create(
            name=name,
            instructions=instructions
        )
    
    def create_question_group(
        self,
        name: str = "Question group test",
        survey: survey_models.Survey = None,
    ) -> survey_models.QuestionGroup:
        """Create a question group object"""

        return survey_models.QuestionGroup.objects.create(
            name=name,
            survey=survey,
        )
    
    def create_question(
        self,
        text: str = "Question test",
        question_group: survey_models.QuestionGroup = None,
    ) -> survey_models.Question:
        """Create a question object"""

        return survey_models.Question.objects.create(
            text=text,
            question_group=question_group,
        )
    
    def create_question_option(
        self,
        text: str = "Question option test",
        question: survey_models.Question = None,
    ) -> survey_models.QuestionOption:
        """Create a question option object"""

        return survey_models.QuestionOption.objects.create(
            text=text,
            question=question,
        )