from rest_framework import status

from core.tests_base.test_views import TestSurveyViewsBase

from survey import models as survey_models
import random


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


class SurveyViewTestCase(TestSurveyViewsBase):
    def setUp(self):
        # Set endpoint
        super().setUp(endpoint="/api/surveys/")

    def test_survey_data(self):
        """Create survey and retrieve its data to validate is the same as created"""

        # Create survey
        survey = self.create_survey()

        # Retrieve survey data
        response = self.client.get(f"{self.endpoint}{survey.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], survey.name)
        self.assertEqual(response.data["instructions"], survey.instructions)

    def test_question_group_data_single(self):
        """
        Create question group and retrieve its data to validate is the same as created
        """

        # Create question group
        question_group = self.create_question_group(
            name="Question group test",
            details="Details question group",
            survey_index=1,
            survey_percentage=0.7,
        )

        # Retrieve question group data
        response = self.client.get(f"{self.endpoint}{question_group.survey.id}/")

        question_group_response = response.data["question_groups"][0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(question_group_response["name"], question_group.name)
        self.assertEqual(question_group_response["details"], question_group.details)
        self.assertEqual(
            question_group_response["survey_index"], question_group.survey_index
        )
        self.assertEqual(
            question_group_response["survey_percentage"],
            question_group.survey_percentage,
        )

    def test_question_group_data_many(self):
        """
        Create many individual question groups and retrieve its data to validate is the
        same as created
        """

        # Create survey
        survey = self.create_survey()

        # Create question groups
        question_groups = []
        for _ in range(1, 6):
            question_groups.append(self.create_question_group(survey=survey))

        # Retrieve question groups data
        response = self.client.get(f"{self.endpoint}{survey.id}/")
        for question_group_index, question_group in enumerate(question_groups):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.data["question_groups"][question_group_index]["name"],
                question_group.name,
            )

    def test_question_group_sorting(self):
        """
        Create three question groups and compare its order its the same as its index
        """

        # Create survey
        survey = self.create_survey()

        # Create question groups
        question_groups = []
        indices = random.sample(range(1, 7), 6)
        for survey_index in indices:
            question_groups.append(
                self.create_question_group(survey=survey, survey_index=survey_index)
            )

        # Retrieve question groups data
        response = self.client.get(f"{self.endpoint}{survey.id}/")
        for question_group_index, question_group in enumerate(question_groups):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.data["question_groups"][question_group_index]["survey_index"],
                question_group_index + 1,
            )

    def test_question_data_single(self):
        """
        Create JUST a question and retrieve its data to validate is the same as created
        """

        # Create question
        question = self.create_question(
            text="Question test", details="Test description", question_group_index=1
        )

        # Retrieve question data
        response = self.client.get(
            f"{self.endpoint}{question.question_group.survey.id}/"
        )

        question_response = response.data["question_groups"][0]["questions"][0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(question_response["text"], question.text)
        self.assertEqual(question_response["details"], question.details)
        self.assertEqual(
            question_response["question_group_index"], question.question_group_index
        )
        self.assertEqual(
            question_response["question_group"], question.question_group.id
        )

    def test_question_data_many(self):
        """
        Create many individual questions and retrieve its data to validate is the same
        as created
        """

        # Create survey
        survey = self.create_survey()

        # Create question group
        question_group = self.create_question_group(survey=survey)

        # Create questions
        questions = []
        for _ in range(1, 6):
            questions.append(self.create_question(question_group=question_group))

        # Retrieve questions data
        response = self.client.get(f"{self.endpoint}{survey.id}/")
        question_response = response.data["question_groups"][0]["questions"]
        for question_index, question in enumerate(questions):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                question_response[question_index]["text"],
                question.text,
            )
            self.assertEqual(
                question_response[question_index]["question_group"],
                question.question_group.id,
            )

    def test_question_sorting(self):
        """
        Create three question and compare its order its the same as its index
        """

        # Create survey
        survey = self.create_survey()

        # Create question group
        question_group = self.create_question_group(survey=survey)

        # Create questions
        questions = []
        indices = random.sample(range(1, 7), 6)
        for question_group_index in indices:
            questions.append(
                self.create_question(
                    question_group=question_group,
                    question_group_index=question_group_index,
                )
            )

        # Retrieve questions data
        response = self.client.get(f"{self.endpoint}{survey.id}/")
        question_response = response.data["question_groups"][0]["questions"]
        for question_index, question in enumerate(questions):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                question_response[question_index]["question_group_index"],
                question_index + 1,
            )

    def test_question_option_data_single(self):
        """
        Create JUST a question option and retrieve its data to validate is the same
        as created
        """

        # Create question option
        question_option = self.create_question_option(
            text="Question option test", question_index=1, points=1
        )

        # Retrieve question option data
        response = self.client.get(
            f"{self.endpoint}{question_option.question.question_group.survey.id}/"
        )

        question_option_response = response.data["question_groups"][0]["questions"][0][
            "options"
        ][0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(question_option_response["text"], question_option.text)
        self.assertEqual(
            question_option_response["question_index"], question_option.question_index
        )
        self.assertEqual(
            question_option_response["question"], question_option.question.id
        )

    def test_question_option_data_many(self):
        """
        Create many individual question options and retrieve its data to validate is the
        same as created
        """

        # Create survey
        survey = self.create_survey()

        # Create question group
        question_group = self.create_question_group(survey=survey)

        # Create question
        question = self.create_question(question_group=question_group)

        # Create question options
        question_options = []
        for i in range(1, 6):
            question_options.append(
                self.create_question_option(
                    question=question,
                    text=f"Question option test {i}",
                    question_index=i,
                    points=1,
                )
            )

        # Retrieve question options data
        response = self.client.get(f"{self.endpoint}{survey.id}/")
        question_option_response = response.data["question_groups"][0]["questions"][0][
            "options"
        ]
        for question_option_index, question_option in enumerate(question_options):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                question_option_response[question_option_index]["text"],
                question_option.text,
            )
            self.assertEqual(
                question_option_response[question_option_index]["question"],
                question_option.question.id,
            )

    def test_question_option_sorting(self):
        """
        Create three question options and compare its order its the same as its index
        """

        # Create survey
        survey = self.create_survey()

        # Create question group
        question_group = self.create_question_group(survey=survey)

        # Create question
        question = self.create_question(question_group=question_group)

        # Create question options
        question_options = []
        indices = random.sample(range(1, 7), 6)
        for question_option_index in indices:
            question_options.append(
                self.create_question_option(
                    question=question,
                    text=f"Question option test {question_option_index}",
                    question_index=question_option_index,
                    points=1,
                )
            )

        # Retrieve question options data
        response = self.client.get(f"{self.endpoint}{survey.id}/")
        question_option_response = response.data["question_groups"][0]["questions"][0][
            "options"
        ]
        for question_option_index, question_option in enumerate(question_options):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                question_option_response[question_option_index]["question_index"],
                question_option_index + 1,
            )
