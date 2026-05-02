import os
import random
from datetime import datetime

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML

BASE_FILE = os.path.basename(__file__)

class Command(BaseCommand):
    help = "Generate a sample PDF using WeasyPrint with advanced CSS features"

    def handle(self, *args, **kwargs):
        self.stdout.write("Generating random data...")
        
        # Generate random data for the template
        rows = []
        statuses = ["Active", "Pending", "Completed", "Failed"]
        for i in range(1, 150):  # 150 rows should be enough to span multiple pages
            rows.append({
                "id": i,
                "name": f"Item {i}",
                "value1": round(random.uniform(10.0, 999.9), 2),
                "value2": random.randint(1, 100),
                "status": random.choice(statuses)
            })

        # Pick a random primary color for the sample
        primary_colors = ["#2c3e50", "#e67e22", "#2980b9", "#8e44ad", "#27ae60"]
        primary_color = random.choice(primary_colors)

        # Resolve logo URL if exists (use file:// for local management command)
        logo_url = None
        logo_path = os.path.join(settings.BASE_DIR, "media", "logo.png")
        if os.path.exists(logo_path):
            logo_url = f"file://{logo_path}"

        context = {
            "title": "WeasyPrint Sample Report",
            "subtitle": "Demonstrating Paged Media CSS in Django",
            "year": datetime.now().year,
            "date": datetime.now().strftime("%B %d, %Y"),
            "rows": rows,
            "primary_color": primary_color,
            "logo_url": logo_url,
        }

        # Render HTML string from template
        self.stdout.write("Rendering HTML template...")
        html_string = render_to_string("survey/group_report.html", context)

        # Output path
        output_dir = os.path.join(settings.BASE_DIR, "media", "temp")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "weasyprint_sample.pdf")

        # Generate PDF
        self.stdout.write("Generating PDF with WeasyPrint...")
        # Since we are not running in a request context, we can construct a fake base_url or file:// URL
        # so that if there were local static assets they would resolve, but here we don't have local images yet.
        base_url = f"file://{settings.BASE_DIR}/"
        
        HTML(string=html_string, base_url=base_url).write_pdf(output_path)

        self.stdout.write(self.style.SUCCESS(f"Successfully generated sample PDF at: {output_path}"))
