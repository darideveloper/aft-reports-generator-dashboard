from django.core.management.base import BaseCommand
from survey.models import TextPDFSummary, QuestionGroup

class Command(BaseCommand):
    help = 'Link QuestionGroups to TextPDFSummary categories based on predefined mapping'

    def handle(self, *args, **options):
        mapping = {
            "CD": [1, 2],
            "TN": [3, 9],
            "CS": [5, 7],
            "IP": [6, 11, 13],
            "TMA": [10, 12],
            "EDC": [4, 8],
        }

        for category_code, topic_indices in mapping.items():
            self.stdout.write(f"Processing category: {category_code}")
            
            # Get all summary records for this category
            summaries = TextPDFSummary.objects.filter(paragraph_type=category_code)
            if not summaries.exists():
                self.stdout.write(self.style.WARNING(f"No TextPDFSummary records found for {category_code}"))
                continue

            # Get question groups for these indices
            qgs = QuestionGroup.objects.filter(survey_index__in=topic_indices)
            if qgs.count() != len(topic_indices):
                found_indices = list(qgs.values_list('survey_index', flat=True))
                missing = set(topic_indices) - set(found_indices)
                self.stdout.write(self.style.ERROR(f"Missing QuestionGroups with indices: {missing} for category {category_code}"))

            for summary in summaries:
                summary.question_groups.set(qgs)
                self.stdout.write(self.style.SUCCESS(f"Linked {qgs.count()} topics to summary ID {summary.id} ({category_code})"))

        self.stdout.write(self.style.SUCCESS("Data initialization completed successfully"))
