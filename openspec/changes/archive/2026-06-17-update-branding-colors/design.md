## Context

The `events` application exposes a public-facing lead registration form rendered at `/events/<slug>/`. This form is designed to be embedded in external websites (like WordPress) using iframes. It also dispatches a transactional confirmation email to successful registrants. Currently, both the form and the email utilize hardcoded blue styling (#2563eb / #1e3a8a) and lack any corporate logo assets. 

To keep the codebase DRY (Don't Repeat Yourself), the branding configuration (colors and logo static path) should not be hardcoded inside multiple template files. Instead, it must be declared centrally and injected dynamically.

## Goals / Non-Goals

**Goals:**
- Centralize and update public event forms and confirmation emails to match the corporate color palette:
  - Primary: Deep Navy (`#0a3c58`)
  - Primary Hover: Dark Accent (`#072a3e`)
  - Background Accent / Border Focus: Soft Sage (`#bcd3cd`)
  - Highlights / Accents: Soft Sand (`#f3d39c`)
- Add the corporate logo (`logo.webp`) to the top of the event form.
- Inject the corporate logo and styling into client-facing registration confirmation emails.
- Ensure the branding configuration is DRY, with colors and logo paths managed in a single central config file.

**Non-Goals:**
- Do not modify database schemas, Django models, or database migrations (branding is constant and static across all events).
- Do not modify the styling of the Django Admin panel or the main dashboard area.
- Do not change any lead capture API validation logic.

## Decisions

### Decision 1: Single Source of Truth for Branding (DRY)
- **Choice**: Define a `BRANDING` dictionary in `project/settings.py` containing the color hex codes and the logo static/remote URL path:
  ```python
  BRANDING = {
      "colors": {
          "primary": "#0a3c58",
          "primary_hover": "#072a3e",
          "secondary": "#bcd3cd",
          "accent": "#f3d39c",
      },
      "logo_path": "https://aft-reports-generator.s3.amazonaws.com/static/core/imgs/logo-leadforward.jpg",
  }
  ```
- **Rationale**: Storing these parameters in settings.py allows us to change colors or logo globally without updating multiple HTML/CSS/Python files.
- **Alternatives Considered**: Storing branding in a separate JSON file or database table. Since branding is static and constant across all events, database tables are overkill and add query overhead, while settings.py is the standard place for global constants in Django.

### Decision 2: Custom Django Template Context Processor
- **Choice**: Implement a custom template context processor `core.context_processors.branding` that automatically exposes the `BRANDING` settings to all template rendering contexts as `branding`.
- **Rationale**: This guarantees that `{{ branding.colors.primary }}` and other brand variables are available in `form.html` (and other templates) without manually updating views to pass them.
- **Alternatives Considered**: Manually adding branding data to individual view contexts. This violates DRY and increases boilerplate.

### Decision 3: Email Logo Path Rendering
- **Choice**: Inject the absolute logo URL and the `BRANDING` settings into the client confirmation email context in `events/views.py`.
- **Rationale**: Email rendering occurs outside of request contexts (so context processors are not run). By reading `settings.BRANDING` directly in `send_event_emails`, we keep the settings DRY. We will construct the absolute URL using the primary host under `settings.ALLOWED_HOSTS` or a fallback.
### Decision 4: Success Confirmation Alert Branding
- **Choice**: Style the success card using the corporate color palette rather than default green colors. The card's background uses a 15% opacity tint of the corporate secondary color (`#bcd3cd26`), its border uses the solid secondary color (`#bcd3cd`), and its text uses the primary brand color (`#0a3c58`).
- **Rationale**: Keeps color scheme consistent with the brand guide while maintaining clean accessibility and contrast.

## Risks / Trade-offs

- **[Risk]** The addition of the logo image changes the initial height of the iframe.
  - *Mitigation*: The form already includes dynamic iframe resizing logic utilizing a `postMessage` listener which fires on the window load event. The height adjustment will automatically be computed and communicated to the parent container.
- **[Risk]** Broken image link in client emails due to dynamic hostname configurations.
  - *Mitigation*: Fall back gracefully to displaying the plain-text event header if the absolute logo URL cannot be resolved or is not configured.
