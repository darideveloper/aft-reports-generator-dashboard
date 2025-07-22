from django.contrib import admin
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


@admin.register(models.QuestionGroup)
class QuestionGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "survey", "survey_percentage", "created_at")
    list_filter = ("survey", "created_at", "updated_at")
    search_fields = ("name", "survey__name")
    readonly_fields = ("created_at", "updated_at")


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


@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("participant", "question_option", "created_at")
    list_filter = (
        "participant__company",
        "question_option__question__question_group__survey",
        "created_at",
        "updated_at",
    )
    search_fields = ("participant__name", "question_option__text")
    readonly_fields = ("created_at", "updated_at")
