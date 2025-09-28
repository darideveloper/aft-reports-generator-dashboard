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
            float: Total
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
        Get the total number of participants for each company in a survey.

        Returns:
            list: List of totals
        """
        reports = models.Report.objects.all()

        totals = [report.total for report in reports]
        return totals

    def get_resulting_paragraphs(self) -> list[dict]:
        """
        DUMMY FUNCTION
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
        total = models.Report.objects.filter(participant=self.participant)[0].total

        # Decide which threshold applies
        if total < 50:
            target_score = 50
        elif total < 70:
            target_score = 70
        else:
            target_score = 100

        # Query texts with that min_score
        queryset = models.TextPDFQuestionGroup.objects.filter(
            min_score=target_score
        ).values_list("text", flat=True)

        # Build the response structure
        result = [
            {"score": total, "text": text}  # always the input score, not the threshold
            for text in queryset
        ]

        return result

    def get_resulting_titles(self) -> dict:
        """
        DUMMY FUNCTION
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
            item["valor"] = (
                models.ReportQuestionGroupTotal.objects.filter(
                    report=self.report, question_group=question_group
                )
                .first()
                .total
            )

        return data

    def get_grade_code(self):
        """
        Return grate code identifier based on total score and quintet of scores

        Returns:
            str: Grade code (MDP, DP, P, AP, MEP)
        """

        all_totals = self.get_all_participants_totals()
        totals_shorted = sorted(all_totals)
        total_count = len(all_totals)
        total_count_quintet_1 = total_count // 5
        total_count_quintet_2 = (total_count * 2) // 5
        total_count_quintet_3 = (total_count * 3) // 5
        total_count_quintet_4 = (total_count * 4) // 5

        # Detect grade code based on total score and quentil of scores
        grade_codes_mins = {
            "MDP": totals_shorted[total_count_quintet_1],
            "DP": totals_shorted[total_count_quintet_2],
            "P": totals_shorted[total_count_quintet_3],
            "AP": totals_shorted[total_count_quintet_4],
            "MEP": totals_shorted[-1],
        }

        # Refresh report to get total
        self.report.refresh_from_db()

        for grade_code, min_total in grade_codes_mins.items():
            if self.report.total <= min_total:
                return grade_code
        return "MEP"
