# Design: Standardize Survey ID Parameter

## Architecture
No structural architectural changes. This is a renaming refactor to ensure consistency across the API surface.

## Implementation Details

### `FormProgressSerializer`
- Rename the `survey` field to `survey_id`.
- Use `source='survey'` to map it back to the model field.

### `FormProgressView`
- **GET**: Expect `survey_id` in `request.query_params`.
- **POST**: Expect `survey_id` in `request.data`.
- **DELETE**: Expect `survey_id` in `request.query_params`.

## Trade-offs
- **Breaking Change**: This changes the API contract for the `progress` endpoint. Since this features was just added and presumably not yet widely consumed by clients (or we are in a dev phase), this is acceptable to fix now rather than later.
