import os
import uuid
import json

from django.test import TestCase
from django.conf import settings
from django.core.files import File

from survey import models as survey_models


class TestSurveyModelBase(TestCase):
    """Test survey models"""

    def __replace_random_string__(self, string: str) -> str:
        """Replace random string with a random string

        Args:
            string (str): The string to replace

        Returns:
            str: The replaced string
        """
        random_string = str(uuid.uuid4())
        return string.replace("{x}", random_string)

    def create_company(
        self,
        name: str = "Company test {x}",
        details: str = "Test description",
        logo: str = "logo.png",
        invitation_code: str = "test {x}",
        is_active: bool = True,
    ) -> survey_models.Company:
        """Create a company object

        Args:
            name (str): The name of the company
            details (str): The details of the company
            logo (str): The logo of the company (inside media folder)
            invitation_code (str): The invitation code of the company
            is_active (bool): Whether the company is active

        Returns:
            survey_models.Company: The created company object
        """

        name = self.__replace_random_string__(name)
        invitation_code = self.__replace_random_string__(invitation_code)

        # Logo path from local media folder
        logo_path = os.path.join(settings.BASE_DIR, "media", logo)

        company = survey_models.Company.objects.create(
            name=name,
            details=details,
            invitation_code=invitation_code,
            is_active=is_active,
        )

        # Upload logo
        with open(logo_path, "rb") as f:
            company.logo.save(logo, File(f))

        return company

    def create_survey(
        self,
        name: str = "Survey test {x}",
        instructions: str = "Test instructions",
    ) -> survey_models.Survey:
        """Create a survey object

        Args:
            name (str): The name of the survey
            instructions (str): The instructions of the survey

        Returns:
            survey_models.Survey: The created survey object
        """

        name = self.__replace_random_string__(name)

        return survey_models.Survey.objects.create(name=name, instructions=instructions)

    def create_question_group_modifier(
        self,
        name: str = "Question group modifier test {x}",
        details: str = "",
        data: dict = {},
    ) -> survey_models.QuestionGroupModifier:
        """Create a question group modifier object

        Args:
            name (str): The name of the question group modifier
            details (str): The details of the question group modifier
            data (dict): The data of the question group modifier

        Returns:
            survey_models.QuestionGroupModifier: The created question group modifier
        """

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
        """Create a question group object

        Args:
            survey (survey_models.Survey): The survey of the question group
            name (str): The name of the question group
            details (str): The details of the question group
            survey_index (int): The index of the question group in the survey
            survey_percentage (float): The percentage of the question group in the survey
            modifiers (list[survey_models.QuestionGroupModifier]): Modifiers of the
                question group.

        Returns:
            survey_models.QuestionGroup: The created question group object
        """

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
        """Create a question object

        Args:
            question_group (survey_models.QuestionGroup): The question group of the
                question.
            text (str): The text of the question
            details (str): The details of the question
            question_group_index (int): The index of the question in the question group

        Returns:
            survey_models.Question: The created question object
        """

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
        """Create a question option object

        Args:
            question (survey_models.Question): The question of the question option
            text (str): The text of the question option
            question_index (int): The index of the question option in the question
            points (int): The points of the question option

        Returns:
            survey_models.QuestionOption: The created question option object
        """

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
        """Create a participant object

        Args:
            name (str): The name of the participant
            email (str): The email of the participant
            gender (str): The gender of the participant
            birth_range (str): The birth range of the participant
            position (str): The position of the participant
            company (survey_models.Company): The company of the participant

        Returns:
            survey_models.Participant: The created participant object
        """

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
        """Create an answer object

        Args:
            participant (survey_models.Participant): The participant of the answer
            question_option (survey_models.QuestionOption): The question option of
                the answer

        Returns:
            survey_models.Answer: The created answer object
        """

        if not participant:
            participant = self.create_participant()

        if not question_option:
            question_option = self.create_question_option()

        return survey_models.Answer.objects.create(
            participant=participant,
            question_option=question_option,
        )

    def create_report(
        self,
        survey: survey_models.Survey = None,
        participant: survey_models.Participant = None,
        status: str = "pending",
    ) -> survey_models.Report:
        """Create a report object

        Args:
            survey (survey_models.Survey): The survey of the report
            participant (survey_models.Participant): The participant of the report
            status (str): The status of the report:
                (pending, processing, completed, error)

        Returns:
            survey_models.Report: The created report object
        """

        if not survey:
            survey = self.create_survey()

        if not participant:
            participant = self.create_participant()

        survey = survey_models.Report.objects.create(
            survey=survey,
            participant=participant,
            status=status,
        )
        survey.save()

        return survey
