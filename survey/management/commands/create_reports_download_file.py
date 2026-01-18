import os
import uuid
import json
import requests
import zipfile

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import File
from django.core.files.uploadedfile import SimpleUploadedFile

from survey import models

from utils import pdf_generator
from utils.screenshots import render_image_from_url
from utils.survey_calcs import SurveyCalcs
from utils.media import get_media_url

BASE_FILE = os.path.basename(__file__)


class Command(BaseCommand):
    help = "Generate next report ready to be processed"

    def handle(self, *args, **kwargs):

        # Process logs
        logs = ""
        temp_dir = os.path.join(settings.BASE_DIR, "media", "temp", "zips")
        os.makedirs(temp_dir, exist_ok=True)

        try:

            # Get next download zip file to be generated
            next_reports_download = (
                models.ReportsDownload.objects.filter(status="pending")
                .order_by("created_at")
                .first()
            )
            if not next_reports_download:
                message = "No reports to download"
                logs += message
                self.stdout.write(self.style.SUCCESS(message))
                return

            # Update status to processing
            next_reports_download.status = "processing"
            next_reports_download.save()

            # Download in temp folder the report pdf files
            pdf_downloaded_paths = []
            for report in next_reports_download.reports.all():
                if not report.pdf_file:
                    message = f"Report {report.id} has no pdf file"
                    logs += message
                    self.stdout.write(self.style.WARNING(message))
                    continue
                pdf_url = get_media_url(report.pdf_file)
                message = f"Downloading pdf file {pdf_url}"
                logs += message
                self.stdout.write(message)
                res = requests.get(pdf_url)
                if res.status_code != 200:
                    message = f"Failed to download pdf file {pdf_url}"
                    logs += message
                    self.stdout.write(self.style.ERROR(message))
                    continue
                pdf_path = os.path.join(temp_dir, f"{str(report)}.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(res.content)
                pdf_downloaded_paths.append(pdf_path)

            # Generate zip file with all pdfs
            message = "Generating zip file with all pdfs"
            logs += message
            self.stdout.write(message)
            zip_path = os.path.join(
                temp_dir, f"reports_download_{next_reports_download.id}.zip"
            )
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for pdf_path in pdf_downloaded_paths:
                    zipf.write(pdf_path, os.path.basename(pdf_path))

            # Delete temp pdf files
            message = "Deleting temp pdf files"
            logs += message
            self.stdout.write(message)
            for pdf_path in pdf_downloaded_paths:
                os.remove(pdf_path)

            # Add file to model
            message = "Adding file to model"
            logs += message
            self.stdout.write(message)
            next_reports_download.zip_file = SimpleUploadedFile(
                name=os.path.basename(zip_path),
                content=open(zip_path, "rb").read(),
                content_type="application/zip",
            )
            next_reports_download.save()

            # Delete temp zip file
            message = "Deleting temp zip file"
            logs += message
            self.stdout.write(message)
            os.remove(zip_path)

            # Update status
            message = "Updating status to completed"
            logs += message
            self.stdout.write(self.style.SUCCESS(message))
            next_reports_download.status = "completed"
            next_reports_download.save()

        except Exception as e:
            # Catch and save error in logs
            message = "Error: " + str(e)
            logs += message
            self.stdout.write(self.style.ERROR(message))
            if next_reports_download:
                next_reports_download.status = "error"

        # Save logs and report download
        if next_reports_download:
            next_reports_download.logs = logs
            next_reports_download.save()
