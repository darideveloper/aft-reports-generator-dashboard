from django.db.models import Avg


from survey import models


class SurveyCalcs:

    def __init__(
        self,
        participant: object,
        survey: object,
        report: object,
    ):
        # Save data
        self.participant = participant
        self.survey = survey
        self.company = participant.company
        self.report = report

    def __get_question_group_total(
        self, question_group: object, participant: object
    ) -> float:
        """
        Get participant total in specific question group, based on answers

        Args:
            question_group: QuestionGroup object
            participant: Participant object

        Returns:
            float: Total (from 0 to 100)
        """

        # Local import to avoid circular import
        from survey.models import Answer, QuestionOption

        # Return points of answers
        options = QuestionOption.objects.filter(
            question__question_group=question_group,
        )
        answers = Answer.objects.filter(
            question_option__question__question_group=question_group,
            participant=participant,
        )

        user_points = sum(answer.question_option.points for answer in answers)
        total_points = sum(option.points for option in options)
        if total_points == 0:
            return 0

        return int(user_points / total_points * 100 * 100) / 100

    def save_report_question_group_totals(self):
        """
        Calculate and save totals for the current report
        """

        # Local import to avoid circular import
        from survey.models import ReportQuestionGroupTotal, QuestionGroup

        # Get question groups of current survey
        question_groups = QuestionGroup.objects.filter(survey=self.survey).order_by(
            "survey_index"
        )

        # Calculate totals for each question group
        for question_group in question_groups:
            total = self.__get_question_group_total(question_group, self.participant)

            report_question_group_total, _ = (
                ReportQuestionGroupTotal.objects.get_or_create(
                    report=self.report,
                    question_group=question_group,
                )
            )
            report_question_group_total.total = total
            report_question_group_total.save()

    def get_participant_total(self) -> float:
        """
        Get the total for the current participant

        Returns:
            float: Total (from 0 to 100%)
        """

        # Local import to avoid circular import
        from survey.models import ReportQuestionGroupTotal

        # Calculate percentage of total in each question group
        question_groups_total = ReportQuestionGroupTotal.objects.filter(
            report=self.report,
        )

        total_score = 0
        for question_group_total in question_groups_total:
            question_group = question_group_total.question_group
            survey_percentage = question_group.survey_percentage
            total = question_group_total.total
            total = total * survey_percentage / 100
            total_score += total

        return total_score

    def get_all_participants_totals(self) -> list:
        """
        Get the total scores of participants in the survey

        Returns:
            list: List of totals
        """
        reports = models.Report.objects.filter()

        totals = [report.total for report in reports]
        return totals

    def get_target_threshold(self, score):
        """
        Get the min score value to recover a text
        Args:
            score: Participant Score on a given Question Group
        Returns:
            int: min score value to recover text
        """
        if score < 50:
            return 50
        elif score < 70:
            return 70
        else:
            return 100

    def get_resulting_paragraphs(self) -> list[dict]:
        """
        Get the resulting paragraphs for a participant in a survey.

        Args:
            participant: Participant object
            survey: Survey object

        Returns:
            list[dict]: List of dictionaries with the resulting paragraphs
                {
                    "score": int,
                    "text": str,
                }
        """
        # Get the participant's report (assuming one report per participant)
        report = models.Report.objects.filter(participant=self.participant).first()
        if not report:
            return []

        result = []

        # Get all group totals
        group_totals = models.ReportQuestionGroupTotal.objects.filter(report=report)

        for group_total in group_totals:
            score = group_total.total
            question_group = group_total.question_group

            # Pick threshold
            threshold = self.get_target_threshold(score)

            # Get corresponding text
            text_entry = models.TextPDFQuestionGroup.objects.filter(
                question_group=question_group, min_score=threshold
            ).first()

            if text_entry:
                result.append(
                    {
                        "score": score,
                        "text": text_entry.text,
                    }
                )

        return result

    def get_resulting_titles(self) -> dict:
        """
        Get the resulting titles for a participant in a survey.

        Args:
            participant: Participant object
            survey: Survey object

        Returns:
            dict: Dictionary with the resulting titles
                {
                    "cultura": {
                        "subtitle": str,
                        "paragraph": str,
                    },
                }
        """

        total = models.Report.objects.filter(participant=self.participant)[0].total

        # Decide which threshold applies
        if total < 50:
            target_score = 49
        elif total < 80:
            target_score = 79
        else:
            target_score = 100

        # Query texts with that min_score
        queryset = models.TextPDFSummary.objects.filter(min_score=target_score).values(
            "paragraph_type", "text"
        )

        result = {}

        for item in queryset:
            paragraph_type = item[
                "paragraph_type"
            ].lower()  # e.g. "Cultura" → "cultura"

            # Split into subtitle + paragraph
            if "|" in item["text"]:
                subtitle, paragraph = item["text"].split("|", 1)
            else:
                subtitle, paragraph = "", item["text"]

            result[paragraph_type] = {
                "subtitle": subtitle.strip(),
                "paragraph": paragraph.strip(),
            }

        return result

    def get_bar_chart_data(self, use_average: bool) -> list[dict]:
        """
        Get the bar chart data for a participant in a survey.

        Args:
            use_average (bool): Whether to use the average or the specific value

        Returns:
            list[dict]: List of dictionaries with the bar chart data
                {
                    "titulo": str,
                    "valor": int,
                    "promedio": float,
                    "minimo": int,
                    "maximo": int,
                    "descripcion": str,
                }
        """

        # get question groups
        question_groups = models.QuestionGroup.objects.filter(
            survey=self.survey
        ).order_by("survey_index")

        # Get title and description from question groups
        data = []
        for question_group in question_groups:
            data.append(
                {
                    "titulo": question_group.name.split("-")[1].strip(),
                    "descripcion": question_group.details_bar_chart,
                }
            )

        # Add max 100 and min 0 to each item
        for item in data:
            item["maximo"] = 100
            item["minimo"] = 0

        # Get avg from category from ReportQuestionGroupTotal
        for item in data:

            question_group = models.QuestionGroup.objects.get(
                name__icontains=item["titulo"]
            )

            # Add item avg to data
            if use_average:
                # Calculate value
                question_group_totals = models.ReportQuestionGroupTotal.objects.filter(
                    question_group=question_group
                )
                avg = question_group_totals.aggregate(total=Avg("total"))["total"]
                item["promedio"] = avg
            else:
                # Get fixed value from question_group
                item["promedio"] = question_group.goal_rate

            # Set value (user group score)
            totals = models.ReportQuestionGroupTotal.objects.filter(
                report=self.report, question_group=question_group
            )
            total = totals.first()
            item["valor"] = total.total

        return data

    def get_grade_code(self):
        """
        Return grate code identifier based on total score and quintet of scores

        Returns:
            str: Grade code (MDP, DP, P, AP, MEP)
        """

        all_totals = self.get_all_participants_totals()
        totals_sorted = sorted(all_totals)
        total_count = len(all_totals)
        
        # Return MEP if no totals
        if total_count < 5:
            return "MEP"

        # Calculate quintile boundaries (percentiles)
        quintile_1_boundary = int(total_count * 0.2)  # 20th percentile
        quintile_2_boundary = int(total_count * 0.4)  # 40th percentile
        quintile_3_boundary = int(total_count * 0.6)  # 60th percentile
        quintile_4_boundary = int(total_count * 0.8)  # 80th percentile

        # Get threshold values for each quintile
        grade_thresholds = {
            "MDP": (
                totals_sorted[quintile_1_boundary]
                if quintile_1_boundary > 0
                else totals_sorted[0]
            ),
            "DP": (
                totals_sorted[quintile_2_boundary]
                if quintile_2_boundary > 0
                else totals_sorted[0]
            ),
            "P": (
                totals_sorted[quintile_3_boundary]
                if quintile_3_boundary > 0
                else totals_sorted[0]
            ),
            "AP": (
                totals_sorted[quintile_4_boundary]
                if quintile_4_boundary > 0
                else totals_sorted[0]
            ),
        }

        # Refresh report to get total
        self.report.refresh_from_db()

        for grade_code, min_total in grade_thresholds.items():
            if self.report.total <= min_total:
                return grade_code
        return "MEP"