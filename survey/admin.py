from django.contrib import admin
from django.utils.html import format_html

from survey import models

from utils.media import get_media_url


# Custom filters for deep filtering relationships (3+ levels)
class SurveyFilter(admin.SimpleListFilter):
    title = "Encuesta"
    parameter_name = "survey"

    def lookups(self, request, model_admin):
        return [(s.id, str(s)) for s in models.Survey.objects.all().order_by("id")]

    def queryset(self, request, queryset):
        if self.value():
            # Check if this is for Answer model (4 levels) or
            # QuestionOption model (3 levels)
            if hasattr(queryset.model, "question_option"):
                # Answer model: question_option__question__question_group__survey
                return queryset.filter(
                    question_option__question__question_group__survey__id=self.value()
                )
            else:
                # QuestionOption model: question__question_group__survey
                return queryset.filter(
                    question__question_group__survey__id=self.value()
                )
        return queryset


class QuestionGroupFilter(admin.SimpleListFilter):
    title = "Grupo de Preguntas"
    parameter_name = "question_group"

    def lookups(self, request, model_admin):
        return [
            (qg.id, str(qg))
            for qg in models.QuestionGroup.objects.all().order_by("survey_index")
        ]

    def queryset(self, request, queryset):
        if self.value():
            # Check if this is for Answer model (3 levels) or
            # QuestionOption model (2 levels)
            if hasattr(queryset.model, "question_option"):
                # Answer model: question_option__question__question_group
                return queryset.filter(
                    question_option__question__question_group__id=self.value()
                )
            else:
                # QuestionOption model: question__question_group
                return queryset.filter(question__question_group__id=self.value())
        return queryset


class QuestionFilter(admin.SimpleListFilter):
    title = "Pregunta"
    parameter_name = "question"

    def lookups(self, request, model_admin):
        return [
            (q.id, str(q))
            for q in models.Question.objects.all().order_by("question_group_index")
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(question_option__question__id=self.value())
        return queryset


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
        SurveyFilter,
        QuestionGroupFilter,
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
    list_display = (
        "participant",
        "survey",
        "status",
        "total",
        "created_at",
        "custom_links",
    )
    list_filter = (
        "participant__company",
        "survey",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = ("participant__name", "survey__name")
    readonly_fields = ("created_at", "updated_at")

    # CUSTOM FIELDS
    def custom_links(self, obj):
        """Create custom Imprimir and Ver buttons"""

        pdf_url = ""
        if obj.status == "completed":
            pdf_url = get_media_url(obj.pdf_file)

        return format_html(
            '<a class="btn my-1 {}" target="_blank" {} {}>Ver Reporte</a>',
            (
                # styles
                "btn-primary"
                if obj.status == "completed"
                else "btn-secondary disabled"
            ),
            f"href={pdf_url}" if pdf_url else "",  # href
            "disabled" if obj.status != "completed" else "",  # disabled
        )


@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("participant", "question_option", "created_at")
    list_filter = (
        "participant__company",
        SurveyFilter,
        QuestionGroupFilter,
        QuestionFilter,
        "question_option",
        "participant",
        "created_at",
        "updated_at",
    )
    search_fields = ("participant__name", "question_option__text")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("participant", "question_option__question__question_group_index")
    list_per_page = 30


@admin.register(models.ReportQuestionGroupTotal)
class ReportQuestionGroupTotalAdmin(admin.ModelAdmin):
    list_display = ("report", "question_group", "total", "created_at")
    list_filter = ("report", "question_group", "created_at", "updated_at")
    search_fields = (
        "report__participant__name",
        "report__participant__email",
        "question_group__name",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("report", "question_group")
    list_per_page = 30


@admin.register(models.TextPDFQuestionGroup)
class TextPDFQuestionGroupAdmin(admin.ModelAdmin):
    list_display = ("text_summary", "question_group", "min_score", "created_at")
    list_filter = ("question_group", "created_at", "updated_at")
    search_fields = ("text", "question_group__name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("question_group", "-min_score")
    
    def text_summary(self, obj):
        return obj.text[:100] + "..."
    
    text_summary.short_description = "Texto"
    text_summary.admin_order_field = "text"


@admin.register(models.TextPDFSummary)
class TextPDFSummaryAdmin(admin.ModelAdmin):
    list_display = ("text_summary", "paragraph_type", "min_score", "created_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("text",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("paragraph_type", "-min_score")
    
    def text_summary(self, obj):
        return obj.text[:100] + "..."
    
    text_summary.short_description = "Texto"
    text_summary.admin_order_field = "text"
