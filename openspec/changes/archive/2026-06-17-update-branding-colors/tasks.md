## 1. Centralized Branding Configuration (DRY)

- [x] 1.1 Add the `BRANDING` configuration dictionary containing colors (`#0a3c58`, `#072a3e`, `#bcd3cd`, `#f3d39c`) and the logo path (`core/imgs/logo.webp`) in [settings.py](file:///develop/django/aft-reports-generator-dashboard/project/settings.py).
- [x] 1.2 Create a custom template context processor in `core/context_processors.py` that loads and returns the `BRANDING` settings.
- [x] 1.3 Register `core.context_processors.branding` inside the `TEMPLATES` definition of [settings.py](file:///develop/django/aft-reports-generator-dashboard/project/settings.py).

## 2. Public Event Form Styles

- [x] 2.1 Update CSS custom variables in the `:root` block of [form.html](file:///develop/django/aft-reports-generator-dashboard/events/templates/events/form.html) to dynamically pull colors from the context variables `{{ branding.colors }}`.
- [x] 2.2 Add a logo display block at the top of the `.form-container` in [form.html](file:///develop/django/aft-reports-generator-dashboard/events/templates/events/form.html) dynamically loading `{% static branding.logo_path %}`.
- [x] 2.3 Adjust input styling, focus borders, and button states in [form.html](file:///develop/django/aft-reports-generator-dashboard/events/templates/events/form.html) to reference the new corporate CSS variables.

## 3. Client Confirmation Emails

- [x] 3.1 Update [client_confirmation.html](file:///develop/django/aft-reports-generator-dashboard/events/templates/events/emails/client_confirmation.html) template styles to use branding variables passed in the context.
- [x] 3.2 In [views.py](file:///develop/django/aft-reports-generator-dashboard/events/views.py) (`send_event_emails`), extract `settings.BRANDING`, construct the absolute logo image URL using the system's hostname, and pass them both into the email context.
- [x] 3.3 Add the logo image element to the top of the email container in [client_confirmation.html](file:///develop/django/aft-reports-generator-dashboard/events/templates/events/emails/client_confirmation.html) referencing the dynamically passed absolute logo URL.
- [x] 3.4 Update the email signature in the footer of [client_confirmation.html](file:///develop/django/aft-reports-generator-dashboard/events/templates/events/emails/client_confirmation.html) to "El equipo LeadForward Global Solutions MJ".

## 4. Verification

- [x] 4.1 Start development server and manually inspect the event form rendering.
- [x] 4.2 Perform a test lead submission to verify form functionality and dynamic resizing.
- [x] 4.3 Inspect the generated outgoing confirmation email layout and color mapping in console/logs or via django mail tools.
