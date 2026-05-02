# Proposal: Add Options API Endpoint

## Why
Currently, dropdown data (like gender, positions, etc.) is hardcoded in the frontend or defined only in `core/choices.py`. To ensure consistency and allow the frontend to dynamically load these options, we need a dedicated API endpoint that returns these choices.

## What Changes
1.  **New API Endpoint**: `/api/options/` (GET) will return centralized choice data from `core/choices.py`.
2.  **No Model Changes**: The endpoint will directly use the constants from `core/choices.py`.

## Impact
- **Affected code**: `survey/views.py`, `project/urls.py`.
- **New capability**: `options-api`.
