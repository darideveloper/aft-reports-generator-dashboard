# Design: Backend Form Persistence Architecture

## Context
The current system allows users to answer surveys but does not save intermediate progress. The frontend is implementing a feature to auto-save progress after each step and restore it upon return. This requires backend support to store this state.

## Goals
1.  **Persistence**: Store the complete state of the frontend form (responses + navigation state) associated with a user's email and survey.
2.  **Restoration**: specific endpoint to fetch this state upon returning to the site.
3.  **Cleanup**: Ability to remove this temporary state once the survey is officially submitted.
4.  **Security**: Basic validation to ensure data integrity and association.

## Decisions

### 1. Data Model (`FormProgress`)
We will create a separate model `FormProgress` instead of modifying `Participant` or `Answer` models. This separates "draft" data from "submitted" data.
-   **Fields**:
    -   `email`: EmailField (Identifier)
    -   `survey`: ForeignKey to Survey (Identifier)
    -   `company`: ForeignKey to Company (Optional, for context)
    -   `current_screen`: Integer (Navigation state)
    -   `data`: JSONField (The actual form state blob)
    -   `expires_at`: DateTime (For automatic cleanup policy)
-   **Uniqueness**: Unique constraint on `(email, survey)`.

### 2. API Design
We will expose a RESTful resource at `/api/progress/`.
-   **GET**: Returns 200 with data if found, 404 if not. Authenticated by querying params `email` + `survey_id`.
-   **POST**: Upsert logic. If record exists for `(email, survey)`, update it; otherwise create.
-   **DELETE**: deletes the record. Used upon final submission.

### 3. Business Logic
-   **Expiration**: Records will default to 30 days expiration.
-   **Completion Check**: We will check `Answer` models to ensure we don't allow "saving progress" for a user who has already completed the survey. If they have, return `400 Bad Request` with error code `ALREADY_SUBMITTED`.
-   **Company Context**: We will attempt to link the `FormProgress` to a `Company` by parsing the `guestCode` from the JSON payload at `data.guestCodeResponse.guestCode`.
-   **Automatic Expiration**: Implement a background mechanism to delete records where `expires_at < NOW()`.
-   **Auto-Cleanup**: When a final survey is submitted, trigger the deletion of the corresponding `FormProgress`.

## Trade-offs
-   **JSON Blob**: Storing the form state as a JSON blob (`data` field) reduces backend validation strictness but maximizes frontend flexibility (`guestCodeResponse`, `emailResponse`, `responses` array) and simplifies the "restore" logic (just send it back).
-   **No User Auth**: We rely on `email` parameter for identification. Since this is for a public survey limit, this is acceptable, matched with the unauthenticated nature of the main flow.

## Risks
-   **Data Consistency**: If the frontend changes its state shape, backend `data` field doesn't care, but restoration might break on frontend if versioning isn't handled. We assume the JSON shape is controlled by the frontend.
