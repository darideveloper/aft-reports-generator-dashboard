from django.conf import settings
from django.templatetags.static import static


def branding(request):
    """
    Template context processor to inject central corporate branding config
    (colors and logo URL) into all HTML template contexts.
    """
    branding_config = getattr(settings, "BRANDING", {})
    logo_path = branding_config.get("logo_path", "")

    logo_url = ""
    if logo_path:
        if logo_path.startswith(("http://", "https://")):
            logo_url = logo_path
        else:
            logo_url = static(logo_path)

    return {
        "branding": branding_config,
        "logo_url": logo_url,
    }
