from core.tests_base.test_models import TestSurveyModelBase
from django.core.management import call_command

from survey import models as survey_models

from utils.media import get_media_url


class GenerateNextReportCommandTestCase(TestSurveyModelBase):
    """Test generate next report command"""

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Create 3 recports with default status
        self.company = self.create_company()
        self.survey = self.create_survey()
        self.participant = self.create_participant(company=self.company)

    def __validate_report(self, report: survey_models.Report):
        """Validate report data

        Args:
            report (survey_models.Report): The report to validate
        """

        # Update report data
        report.refresh_from_db()

        # Validate status
        self.assertEqual(report.status, "completed")
        self.assertIsNotNone(report.pdf_file)

        # Validate url is a valid .pdf link
        pdf_url = get_media_url(report.pdf_file)
        self.assertTrue(pdf_url.endswith(".pdf"))

        # TODO: test cacls

    def __create_report_question_group_totals_data(self):
        """Create report question group totals data

        Returns:
            survey: Survey object
            options: List of QuestionOption objects
        """

        # Generate initial data

        # Single survey
        survey = self.create_survey()

        # Create 4 question groups (but only 2 will be used)
        question_groups = []
        for _ in range(4):
            question_groups.append(
                self.create_question_group(survey=survey, survey_percentage=25)
            )
        question_groups = question_groups[:2]

        # Create 2 questions in each question group
        questions = []
        for question_group in question_groups:
            for _ in range(2):
                questions.append(self.create_question(question_group=question_group))

                # Create 2 options in each question (yes and no)
        options = []
        for question in questions:
            for option in ["yes", "no"]:
                options.append(
                    self.create_question_option(
                        question=question,
                        text=option,
                        points=1 if option == "yes" else 0,
                    )
                )

        return survey, options, question_groups

    def test_many_pending_reports(self):
        """Test with many pending reports
        Expect:
            - The command should update the status of the report to completed
        """

        # Create 3 reports
        reports = []
        for _ in range(3):
            reports.append(
                self.create_report(survey=self.survey, participant=self.participant)
            )

        call_command("generate_next_report")

        # Validate report data
        self.__validate_report(reports[0])

        # Validate other reports are still pending
        for other_report in reports[1:]:
            other_report.refresh_from_db()
            self.assertEqual(other_report.status, "pending")

    def test_single_report(self):
        """Test with a single report
        Expect:
            - The command should update the status of the report to completed
        """

        # Create 1 report
        report = self.create_report(survey=self.survey, participant=self.participant)

        call_command("generate_next_report")

        # Validate report data
        self.__validate_report(report)

    def test_no_pending_reports(self):
        """Test with no pending reports
        Expect:
            - The command should do nothing (skip all reports)
        """

        # Create 2 reports in processing status
        reports = []
        for _ in range(2):
            reports.append(
                self.create_report(
                    survey=self.survey,
                    participant=self.participant,
                    status="processing",
                )
            )

        call_command("generate_next_report")

        # Validate no reports are ready to be processed or completed
        self.assertEqual(
            survey_models.Report.objects.filter(status="pending").count(), 0
        )
        self.assertEqual(
            survey_models.Report.objects.filter(status="completed").count(), 0
        )
        self.assertEqual(survey_models.Report.objects.filter(status="error").count(), 0)

    def test_saved_report_question_group_totals_100(self):
        """Validate question group totals are calculated and saved
        (100% of the questions are correct)"""

        # Create report question group totals data
        survey, options, question_groups = (
            self.__create_report_question_group_totals_data()
        )

        # set CORRECT andser to each question
        selected_options = [
            options[0],  # question 1, yes
            options[2],  # question 2, yes
            options[4],  # question 3, yes
            options[6],  # question 4, yes
        ]
        for option in selected_options:
            self.create_answer(participant=self.participant, question_option=option)

        # Create a report
        report = self.create_report(survey=survey, participant=self.participant)
        call_command("generate_next_report")

        # Get report question group totals
        report_question_group_totals = []
        for question_group in question_groups:
            report_question_group_totals.append(
                survey_models.ReportQuestionGroupTotal.objects.get(
                    report=report, question_group=question_group
                )
            )

        # Validate report question group totals
        for report_question_group_total in report_question_group_totals:

            # Validate aprox value
            self.assertIsNotNone(report_question_group_total.total)
            self.assertEqual(report_question_group_total.total, 100)

        # Validate final score (2 question groups are 0)
        report.refresh_from_db()
        self.assertEqual(report.total, 50)

    def test_saved_report_question_group_totals_50(self):
        """Validate question group totals are calculated and saved
        (50% of the questions are correct)"""

        # Generate initial data
        survey, options, question_groups = (
            self.__create_report_question_group_totals_data()
        )

        # select one answer correct and one answer incorrect
        selected_options = [
            options[0],  # question 1, yes
            options[3],  # question 2, no
            options[4],  # question 3, yes
            options[7],  # question 4, no
        ]
        for option in selected_options:
            self.create_answer(participant=self.participant, question_option=option)

        # Create a report
        report = self.create_report(survey=survey, participant=self.participant)
        call_command("generate_next_report")

        # Get report question group totals
        report_question_group_totals = []
        for question_group in question_groups:
            report_question_group_totals.append(
                survey_models.ReportQuestionGroupTotal.objects.get(
                    report=report, question_group=question_group
                )
            )

        # Validate report question group totals (only 2 with answers)
        for report_question_group_total in report_question_group_totals:
            self.assertEqual(report_question_group_total.total, 50)

        # Validate final score (2 question groups are 0)
        report.refresh_from_db()
        self.assertEqual(report.total, 25)

    def test_saved_report_question_group_totals_0(self):
        """Validate question group totals are calculated and saved
        (0% of the questions are correct)"""

        # Generate initial data
        survey, options, question_groups = (
            self.__create_report_question_group_totals_data()
        )

        # select one answer correct and one answer incorrect
        selected_options = [
            options[1],  # question 1, no
            options[3],  # question 2, no
            options[5],  # question 3, no
            options[7],  # question 4, no
        ]
        for option in selected_options:
            self.create_answer(participant=self.participant, question_option=option)

        # Create a report
        report = self.create_report(survey=survey, participant=self.participant)
        call_command("generate_next_report")

        # Get report question group totals
        report_question_group_totals = []
        for question_group in question_groups:
            report_question_group_totals.append(
                survey_models.ReportQuestionGroupTotal.objects.get(
                    report=report, question_group=question_group
                )
            )

        # Validate report question group totals
        for report_question_group_total in report_question_group_totals:
            self.assertEqual(report_question_group_total.total, 0)

        # Validate final score (2 question groups are 0)
        report.refresh_from_db()
        self.assertEqual(report.total, 0)

    def test_total_is_rounded(self):
        """Validate total is rounded to 2 decimal places"""
        
        # Generate initial data
        survey, options, question_groups = (
            self.__create_report_question_group_totals_data()
        )
        
        # Change wight of first question group to 33.33333
        question_groups[0].survey_percentage = 33.33333
        question_groups[0].save()
        
        # select one answer correct and one answer incorrect
        selected_options = [
            options[0],  # question 1, yes
            options[2],  # question 2, yes
            options[4],  # question 3, yes
            options[6],  # question 4, yes
        ]
        
        for option in selected_options:
            self.create_answer(participant=self.participant, question_option=option)

        # Create a report
        report = self.create_report(survey=survey, participant=self.participant)
        call_command("generate_next_report")

        # Validate total is rounded to 2 decimal places
        report.refresh_from_db()
        decimals = str(report.total).split(".")[1]
        print(decimals, report.total)
        self.assertEqual(len(decimals), 2)