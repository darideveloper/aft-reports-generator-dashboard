from rest_framework import serializers
from .models import Lead


class LeadSubmitSerializer(serializers.ModelSerializer):
    # Honeypot field (hidden field to catch spam bots)
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)
    # Terms and privacy consent (validated then popped — not stored)
    terms = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = Lead
        fields = ("name", "job_position", "email", "phone", "company", "website", "terms")

    def validate(self, attrs):
        event = self.context.get("event")
        if not event:
            raise serializers.ValidationError({"non_field_errors": ["Evento no válido o inactivo."]})

        errors = {}

        # Configuration mapping: (field_name, is_active, is_required, label)
        fields_config = [
            ("name", event.name_active, event.name_required, "Nombre"),
            ("job_position", event.position_active, event.position_required, "Puesto de trabajo"),
            ("email", event.email_active, event.email_required, "Correo electrónico"),
            ("phone", event.phone_active, event.phone_required, "Teléfono"),
            ("company", event.company_active, event.company_required, "Empresa"),
        ]

        for field_name, is_active, is_required, label in fields_config:
            val = attrs.get(field_name)

            if is_active:
                # Validate required field
                if is_required and (val is None or str(val).strip() == ""):
                    errors[field_name] = f"El campo {label.lower()} es requerido."
            else:
                # Clear value if field is inactive for the event
                attrs[field_name] = None

        if errors:
            raise serializers.ValidationError(errors)

        # Terms acceptance — must be truthy (handles missing, false, null)
        if not attrs.get("terms"):
            raise serializers.ValidationError(
                {"terms": "Debe aceptar los Términos y Condiciones y el Aviso de Privacidad."}
            )

        # Pop transient fields so they are not passed to the model's create/save
        attrs.pop("website", None)
        attrs.pop("terms", None)

        return attrs
