import os
import uuid
import json

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import File
from django.db.models import Sum, Count

from survey import models

from utils import pdf_generator
from utils.screenshots import render_image_from_url
from utils.survey_calcs import SurveyCalcs

BASE_FILE = os.path.basename(__file__)


class Command(BaseCommand):
    help = "Generate next report ready to be processed"

    def handle(self, *args, **kwargs):

        # Process logs
        logs = ""

        try:
            # Get oldest report ready to be processed
            reports = models.Report.objects.filter(status="pending").order_by("id")
            if reports.count() == 0:
                message = "No reports ready to be processed"
                logs += f"{message}\n"
                print(message)
                return
            message = f"Found {reports.count()} reports to be processed"
            logs += f"{message}\n"
            print(message)

            # Get oldest report
            report = reports.first()
            message = f"Processing report {report.id}"
            logs += f"{message}\n"
            print(message)

            # Reset main data
            report.status = "processing"
            report.logs = ""
            report.pdf_file = None
            report.total = 0
            report.save()

            participant = report.participant
            survey = report.survey
            name = participant.name

            # Generate survey calcs
            print("Generating survey calcs")
            survey_calcs = SurveyCalcs(
                participant=participant,
                survey=survey,
                report=report,
            )
            survey_calcs.save_report_question_group_totals()

            # Get final score (total)
            total = round(survey_calcs.get_participant_total(), 2)
            report.total = total
            report.save()

            # Temp folder for images
            temp_folder = os.path.join(settings.BASE_DIR, "media", "temp")
            os.makedirs(temp_folder, exist_ok=True)

            # Save company logo as local file
            company = participant.company
            if company.logo:
                logo = company.logo
                logo_path = os.path.join(temp_folder, f"logo-{company.id}.png")
                with open(logo_path, "wb") as f:
                    f.write(logo.read())
            else:
                logo_path = None

            # Save logo in temp folder
            image_random_uuid = str(uuid.uuid4())
            os.makedirs(temp_folder, exist_ok=True)
            image_temp_path = os.path.join(
                temp_folder, f"bar-chart-{image_random_uuid}.jpg"
            )

            # Get data to submit to bar chart
            use_average = participant.company.use_average
            chart_data = survey_calcs.get_bar_chart_data(use_average=use_average)
            json_data = {
                "chart_data": chart_data,
                "use_average": use_average,
            }
            json_raw = json.dumps(json_data)

            # Generate bar chart, also rendering css
            message = "Generating bar chart"
            logs += f"{message}\n"
            print(message)
            url_params = f"?data={json_raw}"
            url = f"{settings.BAR_CHART_ENDPOINT}{url_params}"
            render_image_from_url(url, image_temp_path, width=1000, height=1300)
            
            message = "Calculating company average total"
            logs += f"{message}\n"
            print(message)
            total_sum = models.Report.objects.filter(
                participant__company=company, status="completed"
            ).aggregate(total_sum=Sum("total"), total_count=Count("total"))

            # Fix total None when 0 reports
            if total_sum["total_sum"] is None:
                total_sum["total_sum"] = 0

            # Calculate total
            average_total = total_sum["total_sum"] / total_sum["total_count"]
            average_total = round(average_total, 2)

            # Save total
            company.average_total = average_total
            company.save()
            
            # Generate PDF
            message = "Generating PDF"
            logs += f"{message}\n"
            print(message)

            pdf_path = pdf_generator.generate_report(
                name=name,
                date=report.created_at.strftime("%d/%m/%Y"),
                grade_code=survey_calcs.get_grade_code(),
                final_score=total,
                logo_path=logo_path,
                graph_path=image_temp_path,
                data=survey_calcs.get_all_participants_totals(),
                resulting_paragraphs=survey_calcs.get_resulting_paragraphs(),
                resulting_titles=survey_calcs.get_resulting_titles(),
                company_average_total=company.average_total,
            )

            if not os.path.exists(pdf_path):
                report.status = "error"
                report.logs = logs + "\nEl reporte no fue generado correctamente."
                report.save()
                return

            message = "PDF generated"
            logs += f"{message}\n"
            print(message)

            # Open the file and save it to FileField
            with open(pdf_path, "rb") as f:
                report.pdf_file.save(os.path.basename(pdf_path), File(f), save=True)
            report.status = "completed"
            report.save()
            message = f"Report {report.id} completed"
            logs += f"{message}\n"
            print(message)

            # Save and add logs
            report.logs = logs
            report.save()

        except Exception as e:
            report.status = "error"
            report.logs = logs + f"\nError: {str(e)}"
            report.save()
            print(f"Error: {str(e)}")
            return
