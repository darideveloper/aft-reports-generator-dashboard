## Why

The current `average_total` field in the `Company` model is a cached value that is only updated upon survey submission. This approach can lead to stale data if reports are deleted, modified, or if real-time benchmarking is required. By calculating the group average in real-time, we ensure data consistency and simplify the database schema, aligning the individual report logic with the more robust calculation method used in the group reports.

## What Changes

- **Model Refactoring**: Remove the `average_total` field from the `Company` model in `survey/models.py`. **BREAKING**
- **Logic Removal**: Remove the `average_total` update logic from the `ResponseSerializer` in `survey/serializers.py`.
- **Real-time Calculation**: Implement performance-optimized real-time calculations for both the company average and the global average within the report generation workflow.
- **Utility Update**: Modify `utils/pdf_generator.py` and the `generate_next_report` management command to inject freshly calculated averages instead of cached database values or inline numpy calculations.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `report-persistence`: Requirements for how benchmarking data is stored and retrieved are changing from a static model field to a dynamic calculation.
- `dynamic-pdf-report`: The report generation process must now include a dynamic aggregation step for group benchmarking.

## Impact

- **Database**: Migration required to remove `average_total` from `survey_company`.
- **API/Serializers**: Survey submission will no longer trigger a company-wide aggregation save.
- **Report Generation**: The `generate_report` utility and management command will now perform an aggregation query before rendering the PDF.
- **Performance**: Introduces a database aggregation query per report generation (mitigated by indexing).
