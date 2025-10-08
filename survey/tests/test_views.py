import json
import random

from django.db.models import Avg
from django.core.management import call_command

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
        invitation_code = "test"
        self.create_company(invitation_code=invitation_code)
        payload = {"invitation_code": invitation_code}

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

    def test_question_group_modifiers(self):
        """
        Create question group with modifiers and retrieve its data to validate is the
        same as created
        """

        # Create question group with modifiers
        modifiers = [
            self.create_question_group_modifier(),
            self.create_question_group_modifier(),
        ]
        modifiers_names = [modifier.name for modifier in modifiers]

        question_group = self.create_question_group(
            name="Question group test",
            details="Details question group",
            survey_index=1,
            survey_percentage=0.7,
            modifiers=modifiers,
        )

        # Retrieve question group data
        response = self.client.get(f"{self.endpoint}{question_group.survey.id}/")

        json_data = json.loads(response.content)
        question_group_response = json_data["question_groups"][0]
        self.assertEqual(question_group_response["modifiers"], modifiers_names)

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


class HasAnswerViewTestCase(TestSurveyViewsBase):

    def setUp(self):
        # Set endpoint
        super().setUp(
            endpoint="/api/participant/has-answer/",
            restricted_get=True,
            restricted_post=False,
        )

        self.data = {"email": "test@test.com", "survey_id": 1}

    def test_get_invalid_data(self):
        """Test get request with invalid data"""

        response = self.client.post(self.endpoint, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data["status"])
        self.assertIn("Invalid data", response.data["message"])
        self.assertIn("email", response.data["data"])
        self.assertIn("survey_id", response.data["data"])

    def test_get_invalid_survey_id(self):
        """Test get request with invalid survey id
        Expects status error and "Invalid data"
        """

        # Create pariticipant but not survey or answers
        self.create_participant(email=self.data["email"])

        response = self.client.post(self.endpoint, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data["status"])
        self.assertIn("Invalid data", response.data["message"])
        self.assertIn("survey_id", response.data["data"])
        self.assertNotIn("email", response.data["data"])

    def test_get_invalid_email(self):
        """Test get request with invalid email
        Expects status error and "Invalid data"
        """

        self.data["email"] = "invalid_email"

        # Create survey
        self.create_survey()

        response = self.client.post(self.endpoint, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data["status"])
        self.assertIn("Invalid data", response.data["message"])
        self.assertIn("email", response.data["data"])
        self.assertNotIn("survey_id", response.data["data"])

    def test_get_valid_participant_without_answer(self):
        """Test get request with valid participant without answer
        Expects status ok and "has_answer" false
        """

        # Create participant and survey
        self.create_participant(email=self.data["email"])
        self.create_survey()

        response = self.client.post(self.endpoint, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("ok", response.data["status"])
        self.assertIn("Participant without answer.", response.data["message"])
        self.assertIn("has_answer", response.data["data"])
        self.assertFalse(response.data["data"]["has_answer"])

    def test_get_valid_participant_with_answer(self):
        """Test get request with valid participant with answer
        Expects status error and "has_answer" true
        """

        # Create participant and survey
        participant = self.create_participant(email=self.data["email"])
        self.create_answer(participant=participant)

        response = self.client.post(self.endpoint, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("error", response.data["status"])
        self.assertIn("Participant with answer.", response.data["message"])
        self.assertIn("has_answer", response.data["data"])
        self.assertTrue(response.data["data"]["has_answer"])


class ResponseViewTestCase(TestSurveyViewsBase):

    def setUp(self):
        # Set endpoint
        super().setUp(
            endpoint="/api/response/",
            restricted_get=True,
            restricted_post=False,
        )

        # Setup initial data
        call_command("apps_loaddata")
        call_command("initial_loaddata")
        self.questions, self.options = self.__create_question_and_options()

        answers = [random.choice(self.options) for _ in range(10)]
        answers_ids = [answer.id for answer in answers]

        self.invitation_code = "test"
        self.data = {
            "invitation_code": self.invitation_code,
            "survey_id": 1,
            "participant": {
                "email": "test@test.com",
                "name": "Test User",
                "gender": "m",
                "birth_range": "1946-1964",
                "position": "director",
            },
            "answers": answers_ids,
        }

        # Create company with invitation code
        self.company = self.create_company(invitation_code=self.invitation_code)

        self.question_groups = survey_models.QuestionGroup.objects.all()

    def __create_question_and_options(self) -> tuple:
        """
        Create questions and options in each question group

        Returns:
            tuple: questions and options
        """

        # Set question gorup scores to same percentage
        question_groups = survey_models.QuestionGroup.objects.all()
        for question_group in question_groups:
            question_group.survey_percentage = 100 / len(question_groups)
            question_group.save()

        # Create 10 questions in each question group
        questions = []
        options = []
        for question_group in question_groups:
            for _ in range(10):
                question = self.create_question(question_group=question_group)
                questions.append(question)
                options.append(
                    self.create_question_option(question=question, text="yes", points=1)
                )

        return questions, options

    def test_post_invalid_data(self):
        """Test post request with valid data"""

        response = self.client.post(self.endpoint, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data["status"])
        self.assertIn("Invalid data", response.data["message"])
        self.assertIn("invitation_code", response.data["data"])
        self.assertIn("survey_id", response.data["data"])
        self.assertIn("participant", response.data["data"])
        self.assertIn("answers", response.data["data"])

    def test_post_invalid_invitation_code(self):
        """Test post request with invalid invitation code"""

        self.data["invitation_code"] = "invalid_code"

        response = self.client.post(self.endpoint, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data["status"])
        self.assertIn("Invalid data", response.data["message"])
        self.assertIn("invitation_code", response.data["data"])
        self.assertNotIn("survey_id", response.data["data"])
        self.assertNotIn("participant", response.data["data"])
        self.assertNotIn("answers", response.data["data"])

    def test_post_invalid_survey_id(self):
        """Test post request with invalid survey id"""

        self.data["survey_id"] = 999

        response = self.client.post(self.endpoint, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data["status"])
        self.assertIn("Invalid data", response.data["message"])
        self.assertIn("survey_id", response.data["data"])
        self.assertNotIn("invitation_code", response.data["data"])
        self.assertNotIn("participant", response.data["data"])
        self.assertNotIn("answers", response.data["data"])

    def test_post_missing_participant_data(self):
        """Test post request with missing participant data"""

        self.data["participant"] = {}

        response = self.client.post(self.endpoint, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data["status"])
        self.assertIn("Invalid data", response.data["message"])
        self.assertIn("participant", response.data["data"])
        self.assertIn("email", response.data["data"]["participant"])
        self.assertIn("name", response.data["data"]["participant"])
        self.assertIn("gender", response.data["data"]["participant"])
        self.assertIn("birth_range", response.data["data"]["participant"])
        self.assertIn("position", response.data["data"]["participant"])
        self.assertNotIn("survey_id", response.data["data"])
        self.assertNotIn("invitation_code", response.data["data"])
        self.assertNotIn("answers", response.data["data"])

    def test_post_invalid_answers(self):
        """Test post request with invalid answers"""

        self.data["answers"] = [900, 901, 902]

        response = self.client.post(self.endpoint, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data["status"])
        self.assertIn("Invalid data", response.data["message"])
        self.assertIn("answers", response.data["data"])
        self.assertNotIn("invitation_code", response.data["data"])
        self.assertNotIn("survey_id", response.data["data"])
        self.assertNotIn("participant", response.data["data"])

    def test_post_participant_already_submitted(self):
        """Test post request with participant already submitted"""

        # Delete old survey
        survey_models.Survey.objects.all().delete()

        # Create answer in specific survey
        survey = self.create_survey()
        question_group = self.create_question_group(survey=survey)
        question = self.create_question(question_group=question_group)
        question_option = self.create_question_option(question=question)
        participant = self.create_participant(email=self.data["participant"]["email"])
        self.create_answer(participant=participant, question_option=question_option)

        # Update json data
        self.data["survey_id"] = survey.id
        self.data["answers"] = [question_option.id]

        response = self.client.post(self.endpoint, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data["status"])
        self.assertIn("Invalid data", response.data["message"])
        self.assertIn(
            "This participant has already submitted answers for this survey.",
            str(response.data["data"]),
        )
        self.assertNotIn("invitation_code", response.data["data"])
        self.assertNotIn("survey_id", response.data["data"])
        self.assertNotIn("participant", response.data["data"])
        self.assertNotIn("answers", response.data["data"])

    def test_post_valid_data(self):
        """Test post request with valid data"""

        response = self.client.post(self.endpoint, self.data, format="json")
        participant = survey_models.Participant.objects.get(
            email=self.data["participant"]["email"]
        )

        # Validate response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("ok", response.data["status"])
        self.assertIn(
            "Participant and answers registered successfully", response.data["message"]
        )
        self.assertIn("answers_count", response.data["data"])
        self.assertEqual(response.data["data"]["participant_id"], participant.id)
        self.assertEqual(
            response.data["data"]["answers_count"], len(self.data["answers"])
        )
        self.assertIn("report_id", response.data["data"])

        # Validate data created in database
        participant = survey_models.Participant.objects.get(
            email=self.data["participant"]["email"]
        )
        answers = survey_models.Answer.objects.filter(participant=participant)
        report = survey_models.Report.objects.get(id=response.data["data"]["report_id"])

        self.assertEqual(answers.count(), len(self.data["answers"]))
        self.assertEqual(report.participant, participant)
        self.assertEqual(answers.count(), len(self.data["answers"]))

        # Validate company average total updated
        self.assertEqual(participant.company.average_total, report.total)

    def test_company_average_total_updated(self):
        """Test post request with valid data for many participants"""

        # Create many participants
        for participant_index in range(3):

            # Change participant email and responses
            self.data["participant"]["email"] = f"test{participant_index}@test.com"
            answers = [random.choice(self.options) for _ in range(10)]
            answers_ids = [answer.id for answer in answers]
            self.data["answers"] = answers_ids

            # Create answer
            self.client.post(self.endpoint, self.data, format="json")

        # Validate company average total updated
        reports_average_total = survey_models.Report.objects.filter(
            participant__company=self.company
        ).aggregate(average_total=Avg("total"))["average_total"]
        self.company.refresh_from_db()
        self.assertEqual(reports_average_total, self.company.average_total)

    def test_company_average_many_companies(self):
        """Test post request with valid data for many companies"""

        # Delete old companies
        survey_models.Company.objects.all().delete()

        # Create many participants
        companies = []
        for company_index in range(2):
            invitation_code = f"test{company_index}"
            company = self.create_company(invitation_code=invitation_code)
            companies.append(company)
            for participant_index in range(3):

                # Change participant email and responses
                self.data["participant"][
                    "email"
                ] = f"test{participant_index}-{company_index}@test.com"
                answers = [random.choice(self.options) for _ in range(10)]
                answers_ids = [answer.id for answer in answers]
                self.data["answers"] = answers_ids
                self.data["invitation_code"] = invitation_code

                # Create answer
                self.client.post(self.endpoint, self.data, format="json")

        # Validate company average total updated (for each company)
        for company in companies:
            reports_average_total = survey_models.Report.objects.filter(
                participant__company=company
            ).aggregate(average_total=Avg("total"))["average_total"]
            company.refresh_from_db()
            self.assertEqual(reports_average_total, company.average_total)


class ResponseViewTotalsTestCase(TestSurveyViewsBase):
    """
    Test report totals are generated correctly (question group totals)
    """

    def setUp(self):
        """Set up test data"""
        super().setUp(
            endpoint="/api/response/", restricted_get=True, restricted_post=False
        )

        # Load initial data
        call_command("apps_loaddata")
        call_command("initial_loaddata")
        self.questions, self.options = self.__create_question_and_options()

        # Create apo data
        self.invitation_code = "test"
        self.data = {
            "invitation_code": self.invitation_code,
            "survey_id": 1,
            "participant": {
                "email": "test@test.com",
                "name": "Test User",
                "gender": "m",
                "birth_range": "1946-1964",
                "position": "director",
            },
            "answers": [],
        }
        self.company = self.create_company(invitation_code=self.invitation_code)
        self.participant = self.create_participant(company=self.company)
        self.question_groups = survey_models.QuestionGroup.objects.all()
        self.endpoint = "/api/response/"

    def __create_question_and_options(self) -> tuple:
        """
        Create questions and options in each question group

        Returns:
            tuple: questions and options
        """

        # Set question gorup scores to same percentage
        question_groups = survey_models.QuestionGroup.objects.all()
        for question_group in question_groups:
            question_group.survey_percentage = 100 / len(question_groups)
            question_group.save()

        # Create 10 questions in each question group
        for question_group in question_groups:
            for _ in range(10):
                question = self.create_question(question_group=question_group)
                self.create_question_option(question=question, text="yes", points=1)

        questions = survey_models.Question.objects.all()
        options = survey_models.QuestionOption.objects.all()

        return questions, options

    def __get_selected_options(self, score: int) -> list[int]:
        """
        Get selected options in each question group based on score

        Args:
            score: Score to get selected options

        Returns:
            list[int]: Selected options ids
        """
        selected_options_ids = []
        for question_group in self.question_groups:
            selected_options = self.options.filter(
                points=1, question__question_group=question_group
            )
            selected_options_num = int(score * len(selected_options) / 100)
            selected_options = selected_options[:selected_options_num]
            for option in selected_options:
                selected_options_ids.append(option.id)
        return selected_options_ids

    def __validate_report_totals(self, report: survey_models.Report, score: int):
        """
        Validate report totals are calculated and saved

        Args:
            report (survey_models.Report): report created
            score (int): score to check in report and question group totals
        """

        # Get report question group totals
        for question_group in self.question_groups:
            question_group_total = survey_models.ReportQuestionGroupTotal.objects.get(
                report=report, question_group=question_group
            )

            # Validate aprox value
            self.assertIsNotNone(question_group_total.total)
            self.assertEqual(question_group_total.total, score)

        # Validate final score (2 question groups are 0)
        self.assertEqual(report.total, score)

    def test_totals_100(self):
        """
        Validate question group totals are calculated and saved
        (100% of the questions are correct)
        """

        # set CORRECT andser to each question
        self.data["answers"] = self.__get_selected_options(100)

        # Submit api data
        response = self.client.post(self.endpoint, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        report = survey_models.Report.objects.all().last()

        self.__validate_report_totals(report, 100)

    def test_totals_50(self):
        """
        Validate question group totals are calculated and saved
        (50% of the questions are correct)
        """

        # Select 50% of correct option in each question group
        self.data["answers"] = self.__get_selected_options(50)

        # Submit api data
        response = self.client.post(self.endpoint, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        report = survey_models.Report.objects.all().last()

        self.__validate_report_totals(report, 50)

    def test_totals_0(self):
        """
        Validate question group totals are calculated and saved
        (0% of the questions are correct)
        """

        # Select 0% of correct option in each question group
        self.data["answers"] = self.__get_selected_options(0)

        # Submit api data
        response = self.client.post(self.endpoint, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        report = survey_models.Report.objects.all().last()

        self.__validate_report_totals(report, 0)

    def test_total_is_rounded(self):
        """
        Validate total is rounded to 2 decimal places
        """

        # Select random number of options
        options_to_select = len(self.options) - 1
        random_options = [random.choice(self.options) for _ in range(options_to_select)]
        self.data["answers"] = [option.id for option in random_options]

        # Submit api data
        response = self.client.post(self.endpoint, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        report = survey_models.Report.objects.all().last()

        report_decimals = str(report.total).split(".")[1]
        self.assertEqual(len(report_decimals), 2)
