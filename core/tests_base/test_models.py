import uuid
import json

from django.test import TestCase

from survey import models as survey_models


class TestSurveyModelBase(TestCase):
    """Test survey models"""

    def __replace_random_string__(self, string: str):
        """Replace random string with a random string"""
        random_string = str(uuid.uuid4())
        return string.replace("{x}", random_string)

    def create_company(
        self,
        name: str = "Company test {x}",
        details: str = "Test description",
        logo: str = "test.webp",
        invitation_code: str = "test {x}",
        is_active: bool = True,
    ) -> survey_models.Company:
        """Create a company object"""

        name = self.__replace_random_string__(name)
        invitation_code = self.__replace_random_string__(invitation_code)

        return survey_models.Company.objects.create(
            name=name,
            details=details,
            logo=logo,
            invitation_code=invitation_code,
            is_active=is_active,
        )

    def create_survey(
        self,
        name: str = "Survey test {x}",
        instructions: str = "Test instructions",
    ) -> survey_models.Survey:
        """Create a survey object"""

        name = self.__replace_random_string__(name)

        return survey_models.Survey.objects.create(name=name, instructions=instructions)

    def create_question_group_modifier(
        self,
        name: str = "Question group modifier test {x}",
        details: str = "",
        data: dict = {},
    ) -> survey_models.QuestionGroupModifier:
        """Create a question group modifier object"""

        name = self.__replace_random_string__(name)

        return survey_models.QuestionGroupModifier.objects.create(
            name=name,
            details=details,
            data=json.dumps(data),
        )

    def create_question_group(
        self,
        survey: survey_models.Survey = None,
        name: str = "Question group test {x}",
        details: str = "",
        survey_index: int = 0,
        survey_percentage: float = 0,
        modifiers: list[survey_models.QuestionGroupModifier] = [],
    ) -> survey_models.QuestionGroup:
        """Create a question group object"""

        name = self.__replace_random_string__(name)

        if not survey:
            survey = self.create_survey()

        question_group = survey_models.QuestionGroup.objects.create(
            name=name,
            survey=survey,
            survey_index=survey_index,
            survey_percentage=survey_percentage,
            details=details,
        )

        for modifier in modifiers:
            question_group.modifiers.add(modifier)

        return question_group

    def create_question(
        self,
        question_group: survey_models.QuestionGroup = None,
        text: str = "Question test {x}",
        details: str = "",
        question_group_index: int = 0,
    ) -> survey_models.Question:
        """Create a question object"""

        text = self.__replace_random_string__(text)

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
        question: survey_models.Question = None,
        text: str = "Question option test {x}",
        question_index: int = 0,
        points: int = 0,
    ) -> survey_models.QuestionOption:
        """Create a question option object"""

        text = self.__replace_random_string__(text)

        if not question:
            question = self.create_question()

        return survey_models.QuestionOption.objects.create(
            text=text,
            question=question,
            question_index=question_index,
            points=points,
        )

    def create_participant(
        self,
        name: str = "Test participant {x}",
        email: str = "test{x}@test.com",
        gender: str = "m",
        birth_range: str = "1946-1964",
        position: str = "director",
        company: survey_models.Company = None,
    ) -> survey_models.Participant:
        """Create a participant object"""

        name = self.__replace_random_string__(name)
        email = self.__replace_random_string__(email)

        if not company:
            company = self.create_company()

        return survey_models.Participant.objects.create(
            name=name,
            email=email,
            gender=gender,
            birth_range=birth_range,
            position=position,
            company=company,
        )

    def create_answer(
        self,
        participant: survey_models.Participant = None,
        question_option: survey_models.QuestionOption = None,
    ) -> survey_models.Answer:
        """Create an answer object"""

        if not participant:
            participant = self.create_participant()

        if not question_option:
            question_option = self.create_question_option()

        return survey_models.Answer.objects.create(
            participant=participant,
            question_option=question_option,
        )
