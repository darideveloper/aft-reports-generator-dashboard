# API Reference: Form Persistence (Updated)

This document describes the endpoints for the Form Persistence system, aligned with Frontend requirements.

## Base URL
`/api/progress/`

---

## 1. Retrieve Progress
Retrieve the saved state of a survey to allow a user to continue where they left off.

*   **Method:** `GET`
*   **Query Parameters:**
    *   `email` (string, required): The user's identification.
    *   `survey` (integer, required): The ID of the survey.
*   **Responses:**
    *   **200 OK**: Progress found.
        ```json
        {
          "email": "user@example.com",
          "survey": 1,
          "current_screen": 3,
          "data": { 
            "guestCodeResponse": { "guestCode": "XYZ-123" },
            "emailResponse": { "email": "user@example.com", ... },
            "responses": [...]
          },
          "expires_at": "2026-02-23T12:00:00Z"
        }
        ```
    *   **404 Not Found**: No saved progress for this email/survey.
    *   **400 Bad Request**: Missing required parameters.

---

## 2. Save / Update Progress (Upsert)
Save the current state of the form. This endpoint creates a new record or updates an existing one for the same email and survey.

*   **Method:** `POST`
*   **Body (JSON):**
    ```json
    {
      "email": "user@example.com",
      "survey": 1,
      "current_screen": 4,
      "data": {
        "guestCodeResponse": { "guestCode": "XYZ-123" },
        "emailResponse": { "email": "user@example.com", ... },
        "responses": [...]
      }
    }
    ```
*   **Business Rules:**
    *   **Upsert Logic**: Automatically creates or updates based on the `(email, survey)` pair.
    *   **Block if Completed**: Returns `400 Bad Request` with error code `ALREADY_SUBMITTED` if the user has already submitted final answers for this survey.
    *   **Company Linking**: The backend looks for `data.guestCodeResponse.guestCode` to link the progress to a Company.
    *   **Data Preservation**: The `data` object is persisted in its entirety without stripping fields.
*   **Responses:**
    *   **201 Created / 200 OK**: Success. Returns the saved object.
    *   **400 Bad Request**: Error code `ALREADY_SUBMITTED` or invalid data.

---

## 3. Clear Progress
Delete the temporary progress record once a survey is successfully submitted.

*   **Method:** `DELETE`
*   **Parameters (Query):**
    *   `email` (string): User identification.
    *   `survey` (integer): Survey ID.
*   **Responses:**
    *   **204 No Content**: Success.

---

## Data Model Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `email` | `String` | Participant identifier. |
| `survey` | `Integer` | ID of the Survey. |
| `current_screen` | `Integer` | The last screen/step viewed by the user. |
| `data` | `JSON` | Flexible object containing all form inputs. |
| `expires_at` | `DateTime` | Expiration date for cleanup (defaults to 30 days). |
