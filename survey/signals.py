from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum, Count

from survey import models


@receiver(post_save, sender=models.Report)
def after_report_save(sender, instance, created, **kwargs):

    company = instance.participant.company
    total_sum = models.Report.objects.filter(participant__company=company).aggregate(
        total_sum=Sum("total"), total_count=Count("total")
    )

    # Fix total None when 0 reports
    if total_sum["total_sum"] is None:
        total_sum["total_sum"] = 0

    # Calculate total
    average_total = total_sum["total_sum"] / total_sum["total_count"]

    # Save total
    company.average_total = average_total
    company.save()
