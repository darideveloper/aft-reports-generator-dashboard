## 1. App Setup & Registration

- [x] 1.1 Create Django app directory structure for `events`
- [x] 1.2 Register the `events` app in `INSTALLED_APPS` inside `project/settings.py`
- [x] 1.3 Add routing for `/events/` and `/api/events/` in `project/urls.py`

## 2. Models & Migrations

- [x] 2.1 Implement `Event` and `Lead` models in `events/models.py` with dynamic field configurations and customizable slugs
- [x] 2.2 Create database migrations via `makemigrations` and apply them using `migrate`

## 3. Django Admin Dashboard Integration

- [x] 3.1 Register `Event` and `Lead` models in `events/admin.py`
- [x] 3.2 Add lead list display, search filters, and read-only constraints in the Django admin
- [x] 3.3 Add custom CSV export action for `Lead` objects in Django admin
- [x] 3.4 Configure Jazzmin sidebar layout, ordering, and icons in `project/settings.py` for the new models

## 4. API Endpoints (DRF)

- [x] 4.1 Implement `LeadSubmitSerializer` in `events/serializers.py` to validate input fields dynamically based on the parent event configuration
- [x] 4.2 Create public, CSRF-exempt `LeadSubmitView` API endpoint in `events/views.py` that processes JSON POST requests
- [x] 4.3 Implement spam protection via honeypot field (`website`) check in `LeadSubmitView`
- [x] 4.4 Set up IP-based rate limiting on `LeadSubmitView` using `AnonRateThrottle`

## 5. SMTP Configuration & Mail Templates

- [x] 5.1 Configure global SMTP email settings in `project/settings.py` using environment variables
- [x] 5.2 Add SMTP environment variable placeholders to `.env.dev.example` and `.env.prod.example`
- [x] 5.3 Create HTML templates for admin notifications and client confirmation emails
- [x] 5.4 Implement SMTP sending logic in `LeadSubmitView` wrapped in a non-blocking `try-except` structure

## 6. HTML Form Rendering & Iframe Integration

- [x] 6.1 Create `EventFormView` (a TemplateView decorated with `@xframe_options_exempt`) to render the form at `/events/<slug>/`
- [x] 6.2 Create `form.html` template with responsive layout, field conditional rendering, and clean stylesheet
- [x] 6.3 Add client-side JavaScript to intercept submission, post JSON to the API view, show inline error/success messages, and send scroll height messages via `postMessage`

## 7. Testing & Quality Assurance

- [x] 7.1 Write unit tests in `events/tests.py` verifying dynamic field validation behavior, spam rejection, and SMTP fallback safety
- [x] 7.2 Run and verify tests using `python manage.py test events`
