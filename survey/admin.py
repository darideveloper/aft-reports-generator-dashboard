from django.contrib import admin
from django.utils.html import format_html

from survey import models


@admin.register(models.Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "invitation_code", "is_active", "created_at")
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("name", "invitation_code")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("name", "instructions", "created_at")
    search_fields = ("name", "instructions")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.QuestionGroupModifier)
class QuestionGroupModifierAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(models.QuestionGroup)
class QuestionGroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "survey",
        "survey_index",
        "survey_percentage",
        "created_at",
    )
    list_filter = ("survey", "created_at", "updated_at")
    search_fields = ("name", "survey__name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("survey_index", "name")


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "get_survey_for_admin",
        "question_group",
        "question_group_index",
        "created_at",
    )
    list_filter = (
        "question_group__survey",
        "question_group",
        "created_at",
        "updated_at",
    )
    search_fields = ("text", "question_group__name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("question_group", "question_group_index")


@admin.register(models.QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "question",
        "get_survey_for_admin",
        "get_question_group_for_admin",
        "question_index",
        "points",
        "created_at",
    )
    list_filter = (
        "points",
        "question__question_group__survey",
        "question__question_group",
        "question",
        "created_at",
        "updated_at",
    )
    search_fields = ("text", "question__text")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("question", "question_index")


@admin.register(models.Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "gender",
        "birth_range",
        "position",
        "company",
        "created_at",
    )
    list_filter = (
        "gender",
        "birth_range",
        "position",
        "company",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "email", "company__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("participant", "survey", "created_at", "custom_links")
    list_filter = ("participant__company", "survey", "created_at", "updated_at")
    search_fields = ("participant__name", "survey__name")
    readonly_fields = ("created_at", "updated_at")

    # CUSTOM FIELDS
    def custom_links(self, obj):
        """Create custom Imprimir and Ver buttons"""
        return format_html(
            '<a class="btn btn-primary my-1" href="{}" target="_blank">Ver Reporte</a>',
            f"/report/?survey_id={obj.survey.id}&participant_id={obj.participant.id}",
        )


@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("participant", "question_option", "created_at")
    list_filter = (
        "participant__company",
        "question_option__question__question_group__survey",
        "question_option__question__question_group",
        "question_option__question",
        "question_option",
        "participant",
        "created_at",
        "updated_at",
    )
    search_fields = ("participant__name", "question_option__text")
    readonly_fields = ("created_at", "updated_at")
