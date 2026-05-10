## Context

The current `SurveyCalcsGroup` class provides high-level metrics for a company but lacks the ability to drill down into specific knowledge areas. The user wants to see which areas are performing best and worst across the entire organization.

## Goals / Non-Goals

**Goals:**
- Implement an efficient aggregation method to calculate average scores for each knowledge area across a set of reports.
- Ensure the results are sorted by performance (highest to lowest).
- Support both individual question groups and broader summary categories as "areas".

**Non-Goals:**
- Modifying existing report generation logic.
- Changing how scores are calculated for individual participants.

## Decisions

### 1. ORM-based Aggregation
We will use Django's `annotate` and `values` on the `self.reports` QuerySet to perform the aggregation at the database level.
- **Rationale**: This is significantly faster than fetching all records and calculating averages in Python, especially for companies with many employees.
- **Implementation**: `self.reports.values('reportquestiongrouptotal__question_group').annotate(average=Avg('reportquestiongrouptotal__total')).order_by('-average')`

### 2. Handling Summary Categories
If question group data is not available or if specifically requested, we will aggregate by `ReportSummaryScore`.
- **Rationale**: Summary categories provide a higher-level view that might be preferred for certain reports.

### 3. Return Object vs. ID
The method will return a list of dictionaries containing the model instance (QuestionGroup) and the average score.
- **Rationale**: Returning the instance makes it easier for templates to access area names and other properties without additional queries.

## Risks / Trade-offs

- **[Risk]** Performance on very large datasets → **[Mitigation]** Use database-level aggregation and ensure appropriate indexes exist on `ReportQuestionGroupTotal`.
- **[Risk]** Inconsistent data (some reports missing certain groups) → **[Mitigation]** Average calculation naturally handles missing data by only considering existing records for each group.
