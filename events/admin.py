from django.contrib import admin
import csv
from io import BytesIO
from django.http import HttpResponse
from django.utils.html import format_html
from openpyxl import Workbook
from openpyxl.styles import Font
from .models import Event, Lead


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "is_active",
        "notify_email",
        "invitation_link_display",
        "created_at",
    )
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "slug")
    list_filter = ("is_active", "created_at")

    fieldsets = (
        (None, {
            "fields": (
                "title",
                "slug",
                "is_active",
                "notify_email",
                "invitation_link",
                "invitation_label",
                "event_datetime",
                "duration_minutes",
            )
        }),
        ("Campos del Formulario (Activo)", {
            "fields": (
                "name_active",
                "position_active",
                "email_active",
                "phone_active",
                "company_active",
            )
        }),
        ("Campos del Formulario (Requerido)", {
            "fields": (
                "name_required",
                "position_required",
                "email_required",
                "phone_required",
                "company_required",
            )
        }),
    )

    @admin.display(description="Enlace de invitación", ordering="invitation_link")
    def invitation_link_display(self, obj):
        if not obj.invitation_link:
            return "—"
        return format_html(
            '<a href="{0}" target="_blank" rel="noopener noreferrer">{0}</a>',
            obj.invitation_link,
        )


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone",
        "job_position",
        "company",
        "event",
        "is_spam",
        "created_at",
    )
    list_filter = ("event", "is_spam", "created_at")
    search_fields = ("name", "email", "phone", "job_position", "company")

    # Leads should be read-only in the admin panel to prevent tampering
    readonly_fields = (
        "event",
        "name",
        "email",
        "phone",
        "job_position",
        "company",
        "is_spam",
        "created_at",
    )

    actions = ["export_as_csv", "export_as_excel"]

    _HEADER_COLUMNS = [
        "Nombre",
        "Email",
        "Teléfono",
        "Puesto de trabajo",
        "Empresa",
        "Evento",
        "Spam",
        "Fecha de Registro",
    ]

    def has_add_permission(self, request):
        # Prevent manual creation of leads via admin
        return False

    def _lead_row(self, obj):
        return [
            obj.name or "",
            obj.email or "",
            obj.phone or "",
            obj.job_position or "",
            obj.company or "",
            obj.event.title,
            "Sí" if obj.is_spam else "No",
            obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ]

    @admin.action(description="Exportar registros seleccionados a CSV")
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="leads_registro.csv"'

        writer = csv.writer(response)
        writer.writerow(self._HEADER_COLUMNS)

        for obj in queryset:
            writer.writerow(self._lead_row(obj))

        return response

    @admin.action(description="Exportar registros seleccionados a Excel")
    def export_as_excel(self, request, queryset):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = Lead._meta.verbose_name_plural

        bold_font = Font(bold=True)
        sheet.append(self._HEADER_COLUMNS)
        for cell in sheet[1]:
            cell.font = bold_font

        for obj in queryset:
            sheet.append(self._lead_row(obj))

        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="leads_registro.xlsx"'
        return response
