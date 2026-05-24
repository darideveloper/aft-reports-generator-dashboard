## Context

The system currently relies on a cached `average_total` field in the `Company` model to display the "Media de grupo" in individual reports. This value is updated during survey submission in the `ResponseSerializer`. However, this redundancy creates risks of data inconsistency and complicates the database schema.

## Goals / Non-Goals

**Goals:**
- Eliminate the `average_total` field from the `Company` model and database.
- Centralize the company average calculation logic.
- Ensure the individual report always reflects the most up-to-date group data.
- Maintain performance during PDF generation.

**Non-Goals:**
- Refactoring the Group Report calculation logic (which is already dynamic).
- Modifying how the "Media Global" is calculated.

## Decisions

### 1. Centralize Calculation in `SurveyCalcs`
We will add methods to the `SurveyCalcs` class in `utils/survey_calcs.py` to handle both averages.
- **Rationale**: The `SurveyCalcs` class already handles participant-specific calculations and has access to the necessary context. Centralizing both averages reduces the dependency on `numpy` in the PDF generator and ensures consistency.
- **Implementation**:
  ```python
  def get_company_average(self) -> float:
      from survey.models import Report
      avg = Report.objects.filter(
          participant__company=self.company
      ).aggregate(Avg("total"))["total__avg"]
      return round(avg or 0.0, 2)

  def get_global_average(self) -> float:
      from survey.models import Report
      avg = Report.objects.aggregate(Avg("total"))["total__avg"]
      return round(avg or 0.0, 2)
  ```

### 2. Update Report Generation Workflow
- The `generate_next_report` management command will call these new methods and pass the results to `pdf_generator.generate_report`.
- **Cleanup**: In `utils/pdf_generator.py`, we will remove the inline `np.mean(data)` calculation on Page 3. The `generate_report` function will now receive both `company_average_total` and `global_average_total` as explicit arguments.

### 3. Database Schema Simplification
Remove the `average_total` field from `survey.models.Company`.
- **Rationale**: Removes redundant state and prevents the "stale data" problem.
- **Migration**: A standard Django migration will be generated to drop the column.

## Risks / Trade-offs

- **Performance [Risk]**: Performing an aggregation query for every report generated might increase load if thousands of reports exist for a single company.
- **Mitigation**: Database indexes on `Report.participant` and `Participant.company` make this query highly efficient in PostgreSQL/SQLite. For the current scale, this is negligible compared to the cost of PDF generation itself.
- **Breaking Changes [Risk]**: Any external reporting tools or scripts relying on `Company.average_total` will fail.
- **Mitigation**: Verify that no other parts of the system (like frontend dashboards) use this specific field directly. (Research shows it's primarily used in PDF generation).
