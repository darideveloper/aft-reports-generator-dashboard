## Context

The group report PDF generation process involves aggregating data from multiple individual reports. The current implementation uses a combination of Python-side rounding in `utils/survey_calcs_group.py` and template-side formatting in `survey/templates/survey/pdf/group_report_template.html`. However, several fields, such as maximum/minimum scores and individual ranking indices, are missing explicit formatting, leading to inconsistent display (e.g., "56.5" instead of "56.50").

## Goals / Non-Goals

**Goals:**
- Ensure all numerical scores, averages, and percentages in the group report PDF are displayed with exactly two decimal places.
- Fix specific missing formatting in the "Global Group Index" statistics and the "Ranking nominal" table.
- Maintain consistency between calculated values in Python and rendered values in HTML.

**Non-Goals:**
- Modifying the layout or visual styling of the report beyond number formatting.
- Changing the underlying calculation logic or scoring formulas.
- Updating individual participant reports (this change is scoped to Group Reports).

## Decisions

### 1. Unified Template Formatting
We will apply the Django `|floatformat:2` filter to all relevant numerical context variables in the HTML template.
- **Rationale**: The `floatformat:2` filter is the standard Django way to ensure that a number always shows two decimal places, forcing "50" to "50.00".

### 2. Defensive Rounding in Python
We will verify and ensure that `SurveyCalcsGroup` methods return values rounded to two decimals.
- **Rationale**: While the template filter handles display, rounding in Python ensures that the data is consistent if accessed through other means (e.g., logs or debugging) and prevents floating-point precision issues from being passed to the template.

## Risks / Trade-offs

- **[Risk] Overflowing Table Cells** → Formatting "100" as "100.00" adds characters.
  - **Mitigation**: The current table column widths are sufficient to handle the extra two digits and decimal point.
- **[Risk] Rounding Errors** → Discrepancies between the sum of individual percentages and the total.
  - **Mitigation**: This is an existing mathematical reality in aggregated reports; we will maintain the standard `round(val, 2)` approach which is consistent with the rest of the application.
