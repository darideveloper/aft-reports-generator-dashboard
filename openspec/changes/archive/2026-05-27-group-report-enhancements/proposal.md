## Why

Improving the clarity and depth of the group report by refining template wording and providing more granular details on weakness areas (specific question groups rather than just broad categories). This ensures that the generated PDF is both more readable and provides more actionable insights for users.

## What Changes

- **Template Wording Refinement**: Updated the strength and weakness area descriptions in `group_report_template.html` for better linguistic flow.
- **Granular Weakness Reporting**: Added `weakness_question_groups` to the PDF context to allow reporting on specific question groups.
- **Enhanced Calculation Logic**: Updated `SurveyCalcsGroupTexts` to support toggling between summary-level and question-group-level analysis for extreme areas.
- **Terminology Update**: Updated internal keys to reflect new branding/naming conventions (e.g., "Futuro sustentable e inclusivo").

## Capabilities

### New Capabilities
- `granular-weakness-reporting`: Ability to extract and report weaknesses at the individual question group level for group reports.

### Modified Capabilities
- `group-report-generation`: Updated the group report generation logic to include granular weakness data and improved template wording.

## Impact

- **UI/Templates**: `survey/templates/survey/pdf/group_report_template.html`
- **Business Logic**: `utils/group_report_generator.py` and `utils/survey_calcs_group.py`
- **Data Models**: Affects how survey calculation results are processed and presented in group reports.
