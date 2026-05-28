## Why

The group report PDF currently displays decimal values (scores, averages, and percentages) with inconsistent precision. For example, a value might show as "56.5" instead of the required "56.50". This change ensures that all numerical data in the report follows a uniform two-decimal format, improving readability and professional standards.

## What Changes

- Apply the Django `|floatformat:2` filter to all numerical variables in `survey/templates/survey/pdf/group_report_template.html` that are currently unformatted or inconsistently formatted.
- Specifically target the "Global Group Index" statistics (max/min scores), the "Ranking Nominal" table, and the "Nivel de dominio tecnológico" reference table (ranges) where formatting is currently missing or inconsistent.
- Audit `utils/survey_calcs_group.py` to ensure that data passed to the context is already rounded to two decimal places where appropriate, providing a fallback for the template.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `group-report-generation`: Update the visual representation of scores and percentages to strictly use a two-decimal place format.

## Impact

- **Templates**: `survey/templates/survey/pdf/group_report_template.html`
- **Utilities**: `utils/survey_calcs_group.py`
- **Output**: Group Report PDF files.
