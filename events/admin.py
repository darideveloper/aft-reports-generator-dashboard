from django.contrib import admin
import csv
from django.http import HttpResponse
from django.utils.html import format_html
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

    actions = ["export_as_csv"]

    def has_add_permission(self, request):
        # Prevent manual creation of leads via admin
        return False

    @admin.action(description="Exportar registros seleccionados a CSV")
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="leads_registro.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "Nombre",
            "Email",
            "Teléfono",
            "Puesto de trabajo",
            "Empresa",
            "Evento",
            "Spam",
            "Fecha de Registro",
        ])

        for obj in queryset:
            writer.writerow([
                obj.name or "",
                obj.email or "",
                obj.phone or "",
                obj.job_position or "",
                obj.company or "",
                obj.event.title,
                "Sí" if obj.is_spam else "No",
                obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ])

        return response
