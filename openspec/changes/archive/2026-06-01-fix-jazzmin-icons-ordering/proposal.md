## Why

The Django admin interface using the Jazzmin theme currently has several models that default to generic icons and are missing from the logical sidebar ordering. This makes the admin less intuitive for users and lacks visual polish.

## What Changes

- Update `JAZZMIN_SETTINGS["icons"]` in `project/settings.py` to include specific FontAwesome icons for `survey.ReportSummaryScore`, `survey.GroupReport`, and `authtoken.Token`.
- Standardize `auth` icon keys to lowercase for consistency.
- Update `JAZZMIN_SETTINGS["order_with_respect_to"]` to include all missing models and logical groupings (e.g., `FormProgress` near `Participant`, `auth` at the bottom).

## Capabilities

### New Capabilities
- `admin-ui`: Configuration and iconography for the Django admin Jazzmin theme.

### Modified Capabilities
- None

## Impact

- `project/settings.py`: The `JAZZMIN_SETTINGS` dictionary will be modified.
- Admin Sidebar: Icons and ordering will be updated.
