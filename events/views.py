import logging
import datetime
from datetime import timedelta
from urllib.parse import urlencode

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from django.templatetags.static import static

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle

from .models import Event, Lead
from .serializers import LeadSubmitSerializer

logger = logging.getLogger(__name__)


def _resolve_absolute_url(relative_url):
    if relative_url.startswith(("http://", "https://")):
        return relative_url
    host = "localhost:8000"
    if hasattr(settings, "ALLOWED_HOSTS") and settings.ALLOWED_HOSTS:
        hosts = [h for h in settings.ALLOWED_HOSTS if h and h != "*"]
        if hosts:
            host = hosts[0]
    protocol = "http" if getattr(settings, "DEBUG", False) else "https"
    return f"{protocol}://{host}{relative_url}"


def send_event_emails(lead):
    event = lead.event
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")

    branding = getattr(settings, "BRANDING", {})
    logo_path = branding.get("logo_path", "core/imgs/logo.webp")
    if logo_path.startswith(("http://", "https://")):
        logo_url = logo_path
    else:
        logo_url = _resolve_absolute_url(static(logo_path))

    access_url = None
    if event.invitation_link and event.event_datetime:
        access_relative_url = reverse("events:event-access", kwargs={"slug": event.slug})
        access_url = _resolve_absolute_url(access_relative_url)

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
                {"lead": lead, "event": event, "branding": branding, "logo_url": logo_url, "access_url": access_url}
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


def _escape_ics_text(value):
    if not value:
        return ""
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _build_google_calendar_url(event):
    if not event.event_datetime:
        raise ValueError("Event must have event_datetime set")
    utc_start = event.event_datetime.astimezone(datetime.timezone.utc)
    end_dt = event.event_end_datetime
    if end_dt is None or event.duration_minutes in (0, None):
        utc_end = utc_start
    else:
        utc_end = end_dt.astimezone(datetime.timezone.utc)

    fmt = "%Y%m%dT%H%M%SZ"
    dates = f"{utc_start.strftime(fmt)}/{utc_end.strftime(fmt)}"

    params = {
        "action": "TEMPLATE",
        "text": event.title,
        "dates": dates,
        "ctz": settings.TIME_ZONE,
        "trp": "false",
    }
    if event.invitation_link:
        params["location"] = event.invitation_link

    return "https://www.google.com/calendar/render?" + urlencode(params)


def _build_microsoft_calendar_url(event):
    if not event.event_datetime:
        raise ValueError("Event must have event_datetime set")
    utc_start = event.event_datetime.astimezone(datetime.timezone.utc)
    end_dt = event.event_end_datetime
    if end_dt is None or event.duration_minutes in (0, None):
        utc_end = utc_start
    else:
        utc_end = end_dt.astimezone(datetime.timezone.utc)

    params = {
        "subject": event.title,
        "startdt": utc_start.isoformat(),
        "enddt": utc_end.isoformat(),
        "path": "/calendar/action/compose",
        "rru": "addevent",
    }
    if event.invitation_link:
        params["location"] = event.invitation_link

    return "https://outlook.office.com/calendar/0/deeplink/compose?" + urlencode(params)


def _build_ics_content(event):
    if not event.event_datetime:
        raise ValueError("Event must have event_datetime set")
    utc_start = event.event_datetime.astimezone(datetime.timezone.utc)
    end_dt = event.event_end_datetime
    if end_dt is None or event.duration_minutes in (0, None):
        utc_end = utc_start
    else:
        utc_end = end_dt.astimezone(datetime.timezone.utc)

    fmt = "%Y%m%dT%H%M%SZ"
    dtstamp = timezone.now().astimezone(datetime.timezone.utc).strftime(fmt)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//AFT Dashboard//Eventos//ES",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"DTSTART:{utc_start.strftime(fmt)}",
        f"DTEND:{utc_end.strftime(fmt)}",
        f"SUMMARY:{_escape_ics_text(event.title)}",
        f"UID:{event.slug}@aft-dashboard",
        f"DTSTAMP:{dtstamp}",
    ]
    if event.invitation_link:
        lines.append(f"LOCATION:{_escape_ics_text(event.invitation_link)}")
    lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


@method_decorator(xframe_options_exempt, name="dispatch")
class EventFormView(TemplateView):
    template_name = "events/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        event = get_object_or_404(Event, slug=slug, is_active=True)
        context["event"] = event
        return context


class EventAccessView(TemplateView):
    template_name = "events/access.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = context["event"]
        now = timezone.now()

        time_until_event = event.event_datetime - now
        total_seconds = int(time_until_event.total_seconds())

        context.update({
            "total_seconds": total_seconds,
            "time_until_event": time_until_event,
        })

        if event.event_datetime:
            context["google_calendar_url"] = _build_google_calendar_url(event)
            context["microsoft_calendar_url"] = _build_microsoft_calendar_url(event)
            context["ics_url"] = reverse("events:event-ics", kwargs={"slug": event.slug})

        return context

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug")
        event = get_object_or_404(Event, slug=slug, is_active=True)

        if not event.event_datetime or not event.invitation_link:
            raise Http404("Evento sin enlace de invitación o fecha configurada.")

        now = timezone.now()

        if event.duration_minutes > 0 and event.event_end_datetime and now >= event.event_end_datetime:
            self.template_name = "events/ended.html"
            return self.render_to_response({"event": event})

        now_plus_1h = now + timedelta(hours=1)
        if now_plus_1h >= event.event_datetime:
            return HttpResponseRedirect(event.invitation_link)

        return super().get(request, event=event, *args, **kwargs)


class EventCalendarIcsView(View):
    def get(self, request, slug):
        event = get_object_or_404(Event, slug=slug, is_active=True)
        if not event.event_datetime:
            raise Http404
        content = _build_ics_content(event)
        response = HttpResponse(content, content_type="text/calendar")
        response["Content-Disposition"] = f'attachment; filename="{event.slug}.ics"'
        return response


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
