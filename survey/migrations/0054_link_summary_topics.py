from django.db import migrations

def link_topics(apps, schema_editor):
    TextPDFSummary = apps.get_model('survey', 'TextPDFSummary')
    QuestionGroup = apps.get_model('survey', 'QuestionGroup')
    
    mapping = {
        "CD": [1, 2],
        "TN": [3, 9],
        "CS": [5, 7],
        "IP": [6, 11, 13],
        "TMA": [10, 12],
        "EDC": [4, 8],
    }

    for category_code, topic_indices in mapping.items():
        summaries = TextPDFSummary.objects.filter(paragraph_type=category_code)
        qgs = QuestionGroup.objects.filter(survey_index__in=topic_indices)
        
        for summary in summaries:
            summary.question_groups.set(qgs)

def reverse_link_topics(apps, schema_editor):
    TextPDFSummary = apps.get_model('survey', 'TextPDFSummary')
    for summary in TextPDFSummary.objects.all():
        summary.question_groups.clear()

class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0053_textpdfsummary_question_groups_and_more'),
    ]

    operations = [
        migrations.RunPython(link_topics, reverse_link_topics),
    ]
