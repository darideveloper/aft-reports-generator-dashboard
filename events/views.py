import logging
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.templatetags.static import static

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle

from .models import Event, Lead
from .serializers import LeadSubmitSerializer

logger = logging.getLogger(__name__)


def send_event_emails(lead):
    event = lead.event
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")

    # Resolve branding
    branding = getattr(settings, "BRANDING", {})
    logo_path = branding.get("logo_path", "core/imgs/logo.webp")

    if logo_path.startswith(("http://", "https://")):
        logo_url = logo_path
    else:
        logo_relative_url = static(logo_path)
        if logo_relative_url.startswith(("http://", "https://")):
            logo_url = logo_relative_url
        else:
            host = "localhost:8000"
            if hasattr(settings, "ALLOWED_HOSTS") and settings.ALLOWED_HOSTS:
                hosts = [h for h in settings.ALLOWED_HOSTS if h and h != "*"]
                if hosts:
                    host = hosts[0]
            protocol = "http" if getattr(settings, "DEBUG", False) else "https"
            logo_url = f"{protocol}://{host}{logo_relative_url}"

    # 1. Admin Email Notification
    if event.notify_email:
        admin_subject = f"Nuevo registro: {event.title}"
        try:
            admin_html = render_to_string(
                "events/emails/admin_notification.html",
                {"lead": lead, "event": event, "branding": branding, "logo_url": logo_url, "terms_accepted": True}
            )
            admin_text = strip_tags(admin_html)

            admin_msg = EmailMultiAlternatives(
                subject=admin_subject,
                body=admin_text,
                from_email=from_email,
                to=[event.notify_email],
            )
            admin_msg.attach_alternative(admin_html, "text/html")
            admin_msg.send()
        except Exception as e:
            logger.error(f"Error al enviar notificación de admin por correo: {str(e)}")

    # 2. Client Email Confirmation
    if event.email_active and lead.email:
        client_subject = f"Confirmación de registro: {event.title}"
        try:
            client_html = render_to_string(
                "events/emails/client_confirmation.html",
                {"lead": lead, "event": event, "branding": branding, "logo_url": logo_url}
            )
            client_text = strip_tags(client_html)

            client_msg = EmailMultiAlternatives(
                subject=client_subject,
                body=client_text,
                from_email=from_email,
                to=[lead.email],
            )
            client_msg.attach_alternative(client_html, "text/html")
            client_msg.send()
        except Exception as e:
            logger.error(f"Error al enviar confirmación de cliente por correo: {str(e)}")


@method_decorator(xframe_options_exempt, name="dispatch")
class EventFormView(TemplateView):
    template_name = "events/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        event = get_object_or_404(Event, slug=slug, is_active=True)
        context["event"] = event
        return context


class LeadSubmitView(APIView):
    # Public endpoint: exempt from session auth & CSRF
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AnonRateThrottle]

    def post(self, request, slug):
        event = get_object_or_404(Event, slug=slug, is_active=True)

        serializer = LeadSubmitSerializer(data=request.data, context={"event": event})
        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": "Datos inválidos.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Honeypot Check: website field must be empty for human submissions
        honeypot = request.data.get("website", "")
        if honeypot:
            # Silently intercept bot spam: save as spam but don't send emails
            serializer.save(event=event, is_spam=True)
            return Response(
                {"status": "ok", "message": "Registro recibido exitosamente."},
                status=status.HTTP_201_CREATED,
            )

        # Human submission
        lead = serializer.save(event=event, is_spam=False)

        # Trigger emails with try-except safety
        try:
            send_event_emails(lead)
        except Exception as e:
            logger.error(f"Fallo crítico en el despacho de correos SMTP: {str(e)}")

        return Response(
            {"status": "ok", "message": "Registro recibido exitosamente."},
            status=status.HTTP_201_CREATED,
        )
