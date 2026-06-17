## Context

The current Django application is designed for survey creation and digital competency assessment (via the `survey` app). The user wants to introduce registration forms for marketing events, to be embedded on WordPress sites using iframes. This requires public, iframe-friendly HTML rendering, dynamic predefined field validation, asynchronous submission via a JSON API, and SMTP notification capability.

## Goals / Non-Goals

**Goals:**
- **Decoupled Architecture**: Isolate event form models and logic into a new Django app (`events`).
- **Dynamic Field Configuration**: Allow the admin to toggle visibility and requirement flags for predefined fields (Name, Job Position, Email, Phone, Company) per event.
- **Iframe Support**: Exempt the public form view from `X-Frame-Options` and include a JS height-resizing messaging script.
- **Robust Lead Submission API**: Implement a public, CSRF-exempt JSON API endpoint for registration, utilizing a honeypot field and IP rate-throttling for spam mitigation.
- **SMTP Notification**: Set up global SMTP parameters in Django, and send dual emails (admin notification, client confirmation) without blocking database persistence.

**Non-Goals:**
- **Custom Field Builder**: Dynamic field creation (e.g., creating arbitrary types/labels) is out of scope; only standard predefined fields can be toggled.
- **Lead Self-Service Portal**: Clients will not log in to view or manage registrations; data is managed solely by the admin.
- **Admin CSS Customization**: Custom colors or CSS uploads in the admin panel are excluded. The form will use a clean, neutral theme that adapts to any WordPress design.

## Decisions

### 1. Isolated Django App (`events`) with Codebase Patterns
- **Database PKs**: Following the pattern in `survey/models.py`, all models will explicitly define primary keys using `id = models.AutoField(primary_key=True)` instead of relying on default big autoincrement fields.
- **Spanish Localization**: Since the project is configured for `es-mx`, all models will utilize explicit `verbose_name` and `verbose_name_plural` attributes in Spanish. Dynamic error responses and user notifications will be written in Spanish.
- **Free-text Job Position**: Unlike surveys which map positions to a strict set of choice mappings from `core/choices.py`, marketing registration leads can hold arbitrary job descriptions. The `Lead.job_position` field will be a standard `CharField` (free text) to allow external registrants to enter their exact job titles.

### 2. JSON POST API via Django REST Framework (DRF)
- **Rationale**: Form submissions will be handled by a DRF `APIView` at `/api/events/<slug>/submit/` accepting JSON. This allows the iframe client to post data via standard `fetch()`, validate fields against the event configuration, and receive JSON responses containing precise validation errors or success status. This enables smooth inline updates in the iframe without page reloads.

### 3. CSRF Exemption for Iframe API
- **Rationale**: Third-party cookie blocking in modern browsers (Safari, Chrome, Firefox) prevents reliable CSRF cookie sharing inside cross-origin iframes.
- **Approach**: The DRF endpoint will bypass CSRF verification by clearing its `authentication_classes` (no SessionAuthentication). Security will instead be handled via a honeypot field (`website`) and DRF's `AnonRateThrottle` (throttling requests by IP address).

### 4. Selective X-Frame-Options Exemption & WordPress Integration
- **Rationale**: The django security middleware sends `X-Frame-Options: DENY` by default, blocking iframe rendering.
- **Approach**: We will decorate the `EventFormView` with Django's `@xframe_options_exempt`. Only this public form route is embeddable, while admin pages and survey screens remain fully protected from clickjacking.
- **Iframe Resizing**: The form template will emit a `postMessage` on resize/load. The WordPress admin will embed the form using the following snippet:
  ```html
  <iframe id="event-form-iframe" src="https://your-django-domain.com/events/example-slug/" width="100%" height="400px" style="border:none; overflow:hidden;"></iframe>
  <script>
    window.addEventListener('message', function(e) {
      if (e.data && e.data.type === 'resize-iframe') {
        const iframe = document.getElementById('event-form-iframe');
        if (iframe) {
          iframe.style.height = e.data.height + 'px';
        }
      }
    });
  </script>
  ```

### 5. Resilient Synchronous SMTP Dispatch
- **Rationale**: Setting up Celery or Redis for background mailing would overcomplicate the current codebase setup.
- **Approach**: The SMTP dispatch logic inside the API view will run synchronously but wrapped in a robust `try-except` block. If the SMTP server is down or slow, the `Lead` is saved to the database, a warning is logged, and the API still returns a success code to the user.
- **Timeout Protection**: To prevent requests from hanging, `EMAIL_TIMEOUT = 5` will be configured in `project/settings.py` so mail operations fail fast.

## Risks / Trade-offs

- **[Spam Vulnerability]** → Without CSRF, spam bots can query the API.
  - *Mitigation*: Implement a hidden honeypot input field styled with `display: none;`. Bots filling this field will have their submissions silently flagged or rejected. In addition, `AnonRateThrottle` will restrict repeated submissions from the same IP.
- **[Iframe Layout & Scrollbars]** → The WordPress parent container may cut off the form if the height of the content changes (e.g., validation errors appear).
  - *Mitigation*: Client-side JS will post message payloads (type: `resize-iframe`) with its scroll height. The dynamic script snippet listed in Decision 4 handles this on the parent page.
- **[SMTP Delay]** → Connecting to SMTP in the request lifecycle can add 1-2 seconds of latency to the API response.
  - *Mitigation*: Set a low mail timeout (5s) to guarantee the HTTP response does not time out.
