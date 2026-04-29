# Proposal: Update Summary Scoring Logic

Update the calculation logic for the final summary sections (6 categories) in the PDF report. Instead of using the overall final score, each section will now use an average of scores from specific related topics (QuestionGroups). These calculated averages will be stored in the database for future use.

## Why
Currently, the 6 summary categories on pages 20-21 of the PDF are selected based on the `Report.total` (the overall score). The business requirement is to use specific averages of the 13 available topics to determine which paragraph to show for each category.

## What Changes
1. **Model Updates**:
    - Modify `TextPDFSummary` to include a `ManyToManyField` to `QuestionGroup`. This allows defining which topics contribute to each summary category directly from the admin.
    - Create a new model `ReportSummaryScore` to store the calculated average for each category per report.
2. **Logic Updates**:
    - Update `SurveyCalcs` to calculate these averages based on the mapping.
    - Update `SurveyCalcs.get_resulting_titles` to use these specific category averages instead of the overall `Report.total`.
3. **Data Migration**:
    - Create a script/migration to set up the initial relations between `TextPDFSummary` and `QuestionGroup` based on the provided logic.
    - Populate the relations in the production database (carefully).
4. **PDF Generation**:
    - Ensure the PDF generator receives and uses the correct texts based on the new averages.

## Goals
- Accurate categorization in the PDF based on thematic averages.
- Persistent storage of thematic scores for future analytics.
- Flexibility to update mappings via Django Admin.
