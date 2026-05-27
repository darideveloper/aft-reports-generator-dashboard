## Why

The current OpenSpec documentation contains several placeholders ("TBD") and lacks documentation for recent architectural changes, specifically regarding scoring persistence and dynamic content generation for group reports. This change synchronizes the documentation with the actual implementation to maintain a reliable source of truth.

## What Changes

- **Finalize Specifications**: Replace "TBD" placeholders in `summary-scoring-logic` and `scoring-logic` with accurate purpose statements.
- **Document Scoring Persistence**: Add the `ReportQuestionGroupTotal` model and related logic to the `scoring-logic` specification.
- **Dynamic Content Requirements**: Add requirements for dynamic "Priority Actions" to the `group-report-generation` specification.
- **Detailed Persistence Logic**: Update `company-area-averages` to reflect the specific persistence patterns used in the current refactor.

## Capabilities

### New Capabilities
- `scoring-persistence`: Requirements for the `ReportQuestionGroupTotal` model and how it stores calculated scores for future audits and reporting.
- `dynamic-priority-actions`: Requirements for identifying the two lowest-scoring areas and mapping them to specific action blocks in the PDF report.

### Modified Capabilities
- `summary-scoring-logic`: Update Purpose and clarify category-to-topic mapping based on implemented models.
- `scoring-logic`: Update Purpose and integrate scoring persistence requirements.
- `group-report-generation`: Add requirements for the dynamic priority actions mapping and rounding logic.
- `company-area-averages`: Clarify how averages are calculated using the new persistence models.
- `form-persistence`: Update Purpose and finalize requirements for progress tracking.
- `options-api`: Update Purpose and specify integration with centralized choices.

## Impact

- **Documentation**: All spec files in `openspec/specs/` will be updated to match the codebase.
- **Maintenance**: Future developers will have accurate documentation of the scoring and report generation logic.
