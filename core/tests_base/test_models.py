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
        quantity: int = 1,
    ) -> survey_models.QuestionGroup:
        """Create a question group object"""
        question_groups = [
            survey_models.QuestionGroup.objects.create(
                name=f"Question group test {i}",
                survey=survey,
                survey_index=i,
            )
            for i in range(1, quantity + 1)
        ]
        return question_groups
    
    def create_question(
        self,
        text: str = "Question test",
        question_group: survey_models.QuestionGroup = None,
        quantity: int = 1,
    ) -> survey_models.Question:
        """Create a question object"""
        questions = [
            survey_models.Question.objects.create(
                text=f"Question test {i}",
                question_group=question_group,
                question_group_index=i,
            )
            for i in range(1, quantity + 1)
        ]
        return questions
    
    def create_question_option(
        self,
        text: str = "Question option test",
        question: survey_models.Question = None,
        quantity: int = 1,
    ) -> survey_models.QuestionOption:
        """Create a question option object"""

        question_options = [
            survey_models.QuestionOption.objects.create(
                text=f"Question option test {i}",
                question=question,
                question_index=i,
            )
            for i in range(1, quantity + 1)
        ]
        return question_options