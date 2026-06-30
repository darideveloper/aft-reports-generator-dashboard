from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from survey import models

from utils.group_report_generator import generate_group_report_pdf


class Command(BaseCommand):
    help = "Generate next pending group report PDF"

    def handle(self, *args, **kwargs):
        logs = ""

        try:
            next_group_report = (
                models.GroupReport.objects.filter(status="pending")
                .order_by("created_at")
                .first()
            )
            if not next_group_report:
                message = "No pending group reports to generate"
                logs += message + "\n"
                self.stdout.write(self.style.SUCCESS(message))
                return

            message = f"Processing GroupReport {next_group_report.id}"
            logs += message + "\n"
            self.stdout.write(message)

            next_group_report.status = "processing"
            next_group_report.save()

            reports = next_group_report.reports.all()
            if not reports.exists():
                message = "GroupReport has no reports linked"
                logs += message + "\n"
                self.stdout.write(self.style.ERROR(message))
                next_group_report.status = "error"
                next_group_report.logs = logs
                next_group_report.save()
                return

            company_name = "Reporte Grupal"
            additional_recommendations = None
            if next_group_report.company:
                company_name = next_group_report.company.name
                additional_recommendations = (
                    next_group_report.company.additional_recommendations
                )

            message = f"Generating group report PDF for {reports.count()} reports"
            logs += message + "\n"
            self.stdout.write(message)

            pdf_bytes = generate_group_report_pdf(
                reports=reports,
                company_name=company_name,
                additional_recommendations=additional_recommendations,
            )

            next_group_report.pdf_file.save(
                f"group_report_{next_group_report.id}.pdf",
                ContentFile(pdf_bytes),
                save=True,
            )

            next_group_report.status = "completed"
            message = f"GroupReport {next_group_report.id} completed"
            logs += message + "\n"
            self.stdout.write(self.style.SUCCESS(message))

        except Exception as e:
            message = f"Error: {str(e)}"
            logs += message + "\n"
            self.stdout.write(self.style.ERROR(message))
            if next_group_report:
                next_group_report.status = "error"

        if next_group_report:
            next_group_report.logs = logs
            next_group_report.save()
