## 1. Configuration Setup

- [x] 1.1 Add `SMTP_TEST_TOKEN` environment variable retrieval to `project/settings.py`.
- [x] 1.2 Document and add default or example token values in `.env.dev` and all `.env.example` templates.

## 2. API View Implementation

- [x] 2.1 Implement `ValidateEmailView` in `core/views.py` using Django REST Framework's `APIView`.
- [x] 2.2 Add error checking, token verification logic, and emulated vs. real mail sending handler.

## 3. URL Routing Configuration

- [x] 3.1 Register the `/tests/validate-email/` URL pattern in `project/urls.py`.

## 4. Testing & Verification

- [x] 4.1 Write automated tests in `core/tests.py` verifying successful emulated validation, token failures, missing parameter errors, and SMTP exceptions.
- [x] 4.2 Run unit tests to confirm implementation.
