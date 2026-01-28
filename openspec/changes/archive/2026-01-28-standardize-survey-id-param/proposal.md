# Proposal: Standardize Survey ID Parameter

## Problem
Currently, the API uses inconsistent parameter names for the survey identifier. Some endpoints (like `has-answer` and `response`) use `survey_id`, while the newly added `progress` endpoints use `survey`. This inconsistency confuses API consumers and deviates from the established convention.

## Solution
Update the `FormProgressView` and `FormProgressSerializer` to use `survey_id` instead of `survey` for both input (query params, body) and output representations.

## Impact
- **API Consumers**: Will need to send `survey_id` instead of `survey` when interacting with the progress endpoints.
- **Codebase**: `survey/views.py` and `survey/serializers.py` will be updated.
