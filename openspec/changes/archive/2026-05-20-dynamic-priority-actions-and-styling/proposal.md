# Proposal: Dynamic Priority Actions and Single-Column List Styling

## Overview
This change addresses two distinct improvements in the PDF report generation logic (`group_report_template.html` and related files):
1. **Dynamic Priority Actions**: Modifies the priority actions section (Page 11) to be dynamically generated based on the two lowest-scoring question groups for a given company, instead of using hardcoded recommendations.
2. **Single-Column Name List Styling**: Reverts the previously modified two-column layout for name lists back to a single column, ensuring no awkward overflow occurs. It also introduces proper top margin spacing when a name list directly follows a descriptive paragraph.

## Motivation
Previously, the priority actions printed on the "Señal Prioritaria" page were hardcoded. In reality, actionable feedback should directly target the areas where a company's leadership scored the lowest. Generating these actions dynamically enhances the value and personalization of the report.

Additionally, the two-column layout for participant lists introduced visual and pacing issues. Reverting to a single column while preserving the `break-inside: avoid;` rule keeps the layout clean and readable.

## Scope
- Extract the hardcoded priority actions text into a reusable mapping (`PRIORITY_ACTIONS_MAPPING`).
- Add logic to identify the two question groups with the lowest average scores.
- Match those lowest scores against the mapping to build a dynamic context variable.
- Update the HTML template to iterate over the dynamic priority actions correctly.
- Update the CSS for `.name-list` to remove multi-column definitions and add contextual top margin.

## Implementation Details
- The logic to identify the lowest areas and map them to priority actions is encapsulated within the `SurveyCalcsGroupTexts.get_priority_actions()` method in `utils/survey_calcs_group.py`.
- `PRIORITY_ACTIONS_MAPPING` is contained within the same method to ensure cohesion.
- The `GroupReportPDFView` simply calls this method to supply context for the template, keeping the view lean.
- The `weakness_areas` are safely output in the HTML template by using index variables (`{{ weakness_areas.0|safe }}`).
