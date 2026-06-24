from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models


_http_https_validator = URLValidator(schemes=["http", "https"])


def _validate_http_https_url(value: str) -> None:
    try:
        _http_https_validator(value)
    except ValidationError:
        raise ValidationError(
            "El enlace debe ser una URL http(s) válida."
        )


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name="Título")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug (URL única)")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    notify_email = models.EmailField(
        verbose_name="Correo de notificación",
        help_text="Dirección de correo a la que se enviarán las notificaciones de nuevos registros.",
    )
    invitation_link = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Enlace de invitación",
        help_text=(
            "URL opcional al evento (Zoom, Meet, etc.). Se muestra "
            "únicamente en el correo de confirmación y en la pantalla "
            "de éxito tras el registro."
        ),
        validators=[_validate_http_https_url],
    )
    invitation_label = models.CharField(
        max_length=60,
        blank=True,
        default="",
        verbose_name="Texto del botón de invitación",
        help_text=(
            'Texto del botón de invitación. Si se deja vacío se usa '
            '"Acceder al evento". Solo se muestra si Enlace de '
            "invitación está definido."
        ),
    )

    # Dynamic Field Toggles (Active)
    name_active = models.BooleanField(default=True, verbose_name="Nombre activo")
    position_active = models.BooleanField(default=True, verbose_name="Puesto de trabajo activo")
    email_active = models.BooleanField(default=True, verbose_name="Correo electrónico activo")
    phone_active = models.BooleanField(default=True, verbose_name="Teléfono activo")
    company_active = models.BooleanField(default=False, verbose_name="Empresa activa")

    # Dynamic Field Toggles (Required)
    name_required = models.BooleanField(default=True, verbose_name="Nombre requerido")
    position_required = models.BooleanField(default=True, verbose_name="Puesto de trabajo requerido")
    email_required = models.BooleanField(default=True, verbose_name="Correo electrónico requerido")
    phone_required = models.BooleanField(default=True, verbose_name="Teléfono requerido")
    company_required = models.BooleanField(default=False, verbose_name="Empresa requerida")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def invitation_label_display(self) -> str:
        """Return the trimmed invitation label, or the project default
        when the label is empty or whitespace-only."""
        if self.invitation_label and self.invitation_label.strip():
            return self.invitation_label.strip()
        return "Acceder al evento"


class Lead(models.Model):
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="leads",
        verbose_name="Evento",
    )
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nombre")
    job_position = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Puesto de trabajo",
    )
    email = models.EmailField(blank=True, null=True, verbose_name="Correo electrónico")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Teléfono")
    company = models.CharField(max_length=255, blank=True, null=True, verbose_name="Empresa")
    is_spam = models.BooleanField(default=False, verbose_name="¿Es spam?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Registrado el")

    class Meta:
        verbose_name = "Registro (Lead)"
        verbose_name_plural = "Registros (Leads)"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name or 'Anónimo'} ({self.email or 'Sin correo'}) - {self.event.title}"
