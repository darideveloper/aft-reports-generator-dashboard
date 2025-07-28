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

        return survey_models.Survey.objects.create(name=name, instructions=instructions)

    def create_question_group(
        self,
        survey: survey_models.Survey = None,
        name: str = "Question group test",
        details: str = "",
        survey_index: int = 0,
        survey_percentage: float = 0,
    ) -> survey_models.QuestionGroup:
        """Create a question group object"""

        if not survey:
            survey = self.create_survey()

        return survey_models.QuestionGroup.objects.create(
            name=name,
            survey=survey,
            survey_index=survey_index,
            survey_percentage=survey_percentage,
            details=details,
        )

    def create_question(
        self,
        question_group: survey_models.QuestionGroup,
        text: str = "Question test",
        details: str = "",
        question_group_index: int = 0
    ) -> survey_models.Question:
        """Create a question object"""

        if not question_group:
            question_group = self.create_question_group()

        return survey_models.Question.objects.create(
            text=text,
            question_group=question_group,
            question_group_index=question_group_index,
            details=details,
        )

    def create_question_option(
        self,
        question: survey_models.Question,
        text: str = "Question option test",
        question_index: int = 0,
        points: int = 0,
    ) -> survey_models.QuestionOption:
        """Create a question option object"""

        if not question:
            question = self.create_question()

        return survey_models.QuestionOption.objects.create(
            text=text,
            question=question,
            question_index=question_index,
            points=points,
        )
