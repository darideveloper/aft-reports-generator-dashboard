# Tasks: Add Backend Form Persistence

## 1. Database & Models
- [x] 1.1 Create `FormProgress` model in `survey/models.py`.
    - Fields: `email`, `survey`, `company`, `current_screen`, `data`, timestamps, `expires_at`.
    - Meta: Unique constraint on user/survey.
- [x] 1.2 Generate and run migrations (`python manage.py makemigrations survey`, `migrate`).

## 2. API Implementation
- [x] 2.1 Create `FormProgressSerializer` and `FormProgressRetrieveSerializer` in `survey/serializers.py`.
    - Handle validation logic.
- [x] 2.2 Create `FormProgressView` in `survey/views.py`.
    - Implement `get` (retrieve), `post` (save/upsert), `delete` (clear) methods.
    - Use `survey` as the primary key field for the survey ID.
    - Add logic to return `ALREADY_SUBMITTED` code in `post`.
    - Extract `guestCode` from `data.guestCodeResponse.guestCode` for company linking.
- [x] 2.3 Implement auto-cleanup logic.
    - Background task to remove expired drafts.
    - Hook into final submission to delete progress record.
- [x] 2.4 Register URL endpoint `/api/progress/` in `project/urls.py`.

## 3. Administration
- [x] 3.1 Register `FormProgress` in `survey/admin.py` with filters and search fields.

## 4. Testing
- [x] 4.1 Create `survey/tests/test_form_progress.py`.
    - [x] Test Save/Update flow (Upsert logic).
    - [x] Test Retrieve flow.
    - [x] Test Delete flow.
    - [x] Test Validation: Check for `ALREADY_SUBMITTED` error when user has final answers.
    - [x] Test extraction of `guestCode` from nested JSON structure.

## 5. Verification
- [x] 5.1 Verify creating a progress record via API.
- [x] 5.2 Verify retrieving that record.
- [x] 5.3 Verify deleting that record.
