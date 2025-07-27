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


class SurveyViewTestCase(TestSurveyViewsBase):
    def setUp(self):
        # Set endpoint
        super().setUp(endpoint="/api/survey-detail/")

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

        # Create survey
        survey = self.create_survey()

        # Create question group
        question_group = self.create_question_group(survey=survey)[0]

        # Retrieve question group data
        response = self.client.get(f"{self.endpoint}{survey.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["question_groups"][0]["name"], question_group.name
        )

    def test_question_group_data_many(self):
        """
        Create many individual question groups and retrieve its data to validate is the
        same as created
        """

        # Create survey
        survey = self.create_survey()

        # Create question groups
        question_groups = self.create_question_group(survey=survey, quantity=5)

        # Retrieve question groups data
        for i, question_group in enumerate(question_groups):
            response = self.client.get(f"{self.endpoint}{survey.id}/")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.data["question_groups"][i]["name"], question_group.name
            )

    def test_question_group_sorting(self):
        """
        Create three question groups and compare its order its the same as its index
        """

        # Create survey
        survey = survey_models.Survey.objects.create(
            name="Survey test",
            details="Test description",
            company=self.company_1,
        )

        # Create question groups
        question_groups = [
            survey_models.QuestionGroup.objects.create(
                name=f"Question group test {i}",
                survey=survey,
            )
            for i in range(1, 4)
        ]

        # Retrieve question groups data
        for i, question_group in enumerate(question_groups):
            response = self.client.get(f"{self.endpoint}{question_group.id}/")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["survey_index"], i)

    def test_question_data_single(self):
        """
        Create JUST a question and retrieve its data to validate is the same as created
        """

        # Create survey
        survey = survey_models.Survey.objects.create(
            name="Survey test",
            details="Test description",
            company=self.company_1,
        )

        # Create question group
        question_group = survey_models.QuestionGroup.objects.create(
            name="Question group test",
            survey=survey,
        )

        # Create question
        question = survey_models.Question.objects.create(
            text="Question test",
            question_group=question_group,
        )

        # Retrieve question data
        response = self.client.get(f"{self.endpoint}{question.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], question.text)
        self.assertEqual(response.data["question_group"], question.question_group.id)

    def test_question_data_many(self):
        """
        Create many individual questions and retrieve its data to validate is the same
        as created
        """

        # Create survey
        survey = survey_models.Survey.objects.create(
            name="Survey test",
            details="Test description",
            company=self.company_1,
        )

        # Create question group
        question_group = survey_models.QuestionGroup.objects.create(
            name="Question group test",
            survey=survey,
        )

        # Create questions
        questions = [
            survey_models.Question.objects.create(
                text=f"Question test {i}",
                question_group=question_group,
            )
            for i in range(1, 6)
        ]

        # Retrieve questions data
        for question in questions:
            response = self.client.get(f"{self.endpoint}{question.id}/")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["text"], question.text)
            self.assertEqual(
                response.data["question_group"], question.question_group.id
            )

    def test_question_sorting(self):
        """
        Create three question and compare its order its the same as its index
        """

        # Create survey
        survey = survey_models.Survey.objects.create(
            name="Survey test",
            details="Test description",
            company=self.company_1,
        )

        # Create question group
        question_group = survey_models.QuestionGroup.objects.create(
            name="Question group test",
            survey=survey,
        )

        # Create questions
        questions = [
            survey_models.Question.objects.create(
                text=f"Question test {i}",
                question_group=question_group,
            )
            for i in range(1, 4)
        ]

        # Retrieve questions data
        for i, question in enumerate(questions):
            response = self.client.get(f"{self.endpoint}{question.id}/")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["question_group_index"], i)

    def test_question_own_question_group(self):
        """
        Create three questions by question_group and compare its queston group
        """
        pass

    def test_question_option_data_single(self):
        """
        Create JUST a question option and retrieve its data to validate is the same
        as created
        """

        # Create survey
        survey = survey_models.Survey.objects.create(
            name="Survey test",
            details="Test description",
            company=self.company_1,
        )

        # Create question group
        question_group = survey_models.QuestionGroup.objects.create(
            name="Question group test",
            survey=survey,
        )

        # Create question
        question = survey_models.Question.objects.create(
            text="Question test",
            question_group=question_group,
        )

        # Create question option
        question_option = survey_models.QuestionOption.objects.create(
            text="Question option test",
            question=question,
        )

        # Retrieve question option data
        response = self.client.get(f"{self.endpoint}{question_option.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], question_option.text)
        self.assertEqual(response.data["question"], question_option.question.id)

    def test_question_option_data_many(self):
        """
        Create many individual question options and retrieve its data to validate is the
        same as created
        """

        # Create survey
        survey = survey_models.Survey.objects.create(
            name="Survey test",
            details="Test description",
            company=self.company_1,
        )

        # Create question group
        question_group = survey_models.QuestionGroup.objects.create(
            name="Question group test",
            survey=survey,
        )

        # Create question
        question = survey_models.Question.objects.create(
            text="Question test",
            question_group=question_group,
        )

        # Create question options
        question_options = [
            survey_models.QuestionOption.objects.create(
                text=f"Question option test {i}",
                question=question,
            )
            for i in range(1, 6)
        ]

        # Retrieve question options data
        for question_option in question_options:
            response = self.client.get(f"{self.endpoint}{question_option.id}/")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["text"], question_option.text)
            self.assertEqual(response.data["question"], question_option.question.id)

    def test_question_option_sorting(self):
        """
        Create three question options and compare its order its the same as its index
        """

        # Create survey
        survey = survey_models.Survey.objects.create(
            name="Survey test",
            details="Test description",
            company=self.company_1,
        )

        # Create question group
        question_group = survey_models.QuestionGroup.objects.create(
            name="Question group test",
            survey=survey,
        )

        # Create question
        question = survey_models.Question.objects.create(
            text="Question test",
            question_group=question_group,
        )

        # Create question options
        question_options = [
            survey_models.QuestionOption.objects.create(
                text=f"Question option test {i}",
                question=question,
            )
            for i in range(1, 4)
        ]

        # Retrieve question options data
        for i, question_option in enumerate(question_options):
            response = self.client.get(f"{self.endpoint}{question_option.id}/")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["question_index"], i)

    def test_option_own_question(self):
        """
        Create three option by question and compare its queston
        """
        pass
