# Capability: API Parameter Consistency

## ADDED Requirements

### Requirement: Use `survey_id` for progress endpoints
 The `progress` endpoints MUST use `survey_id` as the parameter name for the survey identifier in all methods (GET, POST, DELETE) to match other API endpoints.

#### Scenario: Helper sends GET request with `survey_id`
 Given a user exists with email "test@example.com" and survey id 1
 And the user has progress saved
 When I make a GET request to `/api/progress/` with params `email="test@example.com"` and `survey_id=1`
 Then the response status should be 200 OK
 And the response body should contain the progress data

#### Scenario: Helper sends POST request with `survey_id`
 Given a valid payload with `email`, `survey_id`, and `data`
 When I make a POST request to `/api/progress/`
 Then the progress should be saved
 And the response should contain `"survey_id": 1` (or the actual ID)

#### Scenario: Helper sends DELETE request with `survey_id`
 Given a user exists with progress
 When I make a DELETE request to `/api/progress/` with params `email="test@example.com"` and `survey_id=1`
 Then the response status should be 204 No Content
 And the progress should be deleted
