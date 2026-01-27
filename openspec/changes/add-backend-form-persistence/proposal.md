# Change: Add Backend Form Persistence

## Why
The frontend requires a way to save and restore user progress in the multi-step report generator form. Currently, if a user closes the browser or loses connectivity, they lose all progress. A "continue" system is needed to allow users to resume from their last completed step by identifying themselves via email.

## What Changes
We will implement a backend "Form Persistence" system that includes:
- **New Data Model**: `FormProgress` to store in-progress form data (responses, current screen, etc.) identified by email and survey.
- **New API Endpoints**:
  - `GET /api/progress/`: Retrieve saved progress.
  - `POST /api/progress/`: Save or update progress.
  - `DELETE /api/progress/`: Clear progress after completion.
- **Admin Integration**: Manage `FormProgress` records via Django Admin.
- **Business Logic**:
  - Auto-expiration of progress validation.
  - preventing progress save for completed surveys.
  - auto-association with Company based on invitation code.

## Impact
- **New App/Files**:
  - `survey/models.py` (modified)
  - `survey/views.py` (modified)
  - `survey/serializers.py` (modified)
  - `survey/admin.py` (modified)
  - `project/urls.py` (modified)
  - `survey/tests/test_form_progress.py` (new)
- **Database**: New table for `FormProgress` model.
- **API**: New endpoints under `/api/progress/`.
