# Design: Summary Scoring Logic Update

## Architecture
The system currently calculates `ReportQuestionGroupTotal` for each topic. We will extend this to calculate aggregate scores for summary categories.

### 1. Database Schema

#### `TextPDFSummary` (Modified)
- `question_groups`: `ManyToManyField(QuestionGroup)`
  - *Purpose*: To define which topics belong to each summary category (e.g., "Cultura Digital" uses Topics 1 and 2).

#### `ReportSummaryScore` (New)
- `report`: `ForeignKey(Report)`
- `paragraph_type`: `CharField` (using `TextPDFSummary.TEXT_TYPE_CHOICES`)
- `score`: `FloatField`
- *Purpose*: Persistent storage of the average score calculated for a specific category in a specific report.

### 2. Calculation Logic (`SurveyCalcs`)
- `save_report_summary_scores()`:
    1. Iterate over distinct `paragraph_type` in `TextPDFSummary`.
    2. For each type, get the related `QuestionGroup`s from **all** `TextPDFSummary` records of that type (collecting a unique set).
    3. Retrieve the scores from `ReportQuestionGroupTotal` for these groups.
    4. Calculate the average.
    5. **Round the result to 2 decimal places** (e.g., `round(avg, 2)`).
    6. Save/Update `ReportSummaryScore`.

- `get_resulting_titles()`:
    - Instead of querying `TextPDFSummary.objects.filter(min_score__lte=total)`, it will:
        1. Retrieve the `ReportSummaryScore` for the category (`score`).
        2. Filter `TextPDFSummary.objects.filter(paragraph_type=type, min_score__gte=score)`.
        3. Order by `min_score` ascending (`order_by('min_score')`).
        4. Select the first record (the smallest threshold that is >= score).

### 3. Topic Mapping
Based on user input:
- **CD (Cultura digital)**: Topics 1, 2
- **TN (Tecnología y negocios)**: Topics 3, 9
- **CS (Ciber seguridad)**: Topics 5, 7
- **IP (Impacto personal)**: Topics 6, 11, 13
- **TMA (Tecnología y medio ambiente)**: Topics 10, 12
- **EDC (Ecosistema digital de colaboración)**: Topics 4, 8

### 4. PDF Rendering Sequence
The summary categories must be rendered in the PDF pages 20 and 21 in the following strict order:
1. **CD** (Cultura digital)
2. **TN** (Tecnología y negocios)
3. **CS** (Ciber seguridad)
4. **IP** (Impacto personal)
5. **TMA** (Tecnología y medio ambiente)
6. **EDC** (Ecosistema digital de colaboración)

## Testing Strategy

### 1. Unit Tests (`SurveyCalcs`)
- **Averaging Logic**: Verify `save_report_summary_scores` correctly calculates the average of related `QuestionGroup` scores, including rounding and float handling.
- **Retrieval Logic**: Verify `get_resulting_titles` correctly retrieves scores from `ReportSummaryScore` and falls back to appropriate defaults if scores are missing.
- **Mapping Logic**: Verify that changing mappings in `TextPDFSummary` immediately reflects in subsequent calculations.

### 2. Model & Admin Tests
- **Persistence**: Verify `ReportSummaryScore` records are created/updated correctly and linked to the correct `Report`.
- **ManyToMany Integrity**: Verify that `TextPDFSummary` can correctly associate with multiple `QuestionGroup`s.

### 3. Integration Tests
- **Differentiated PDF Summary**: A test with high scores in some categories and low scores in others to verify that the PDF correctly displays different summary levels for each category simultaneously.
- **Command Workflow**: Ensure `generate_next_report` executes the calculation step before PDF generation.

### 4. Edge Cases
- **Missing Mapping**: Ensure the system handles categories with no mapped topics without crashing (falling back to 0 or overall total).
- **Missing Scores**: Handle cases where a topic exists but has no score for a specific report.
- **Re-generation**: Verify that re-running a report updates existing `ReportSummaryScore` instead of creating duplicates.

### 5. Migration Verification
- Ensure the initial data migration correctly sets up the default 6-to-13 mapping based on the design.

## Implementation Strategy
- **Step 1**: Models. Add field to `TextPDFSummary` and create `ReportSummaryScore`.
- **Step 2**: Migration/Script. Associate the 13 topics with the 6 summary types in the DB.
- **Step 3**: Logic. Update `SurveyCalcs` to perform calculations and storage.
- **Step 4**: Report Command. Ensure `generate_next_report` triggers the new calculation.
- **Step 5**: Testing. Verify PDF outputs correctly reflect these averages.

## Trade-offs
- **Flexibility**: Moving the mapping to a `ManyToManyField` allows admins to change it without code changes in the future.
- **Redundancy**: Storing `ReportSummaryScore` adds rows to the DB but simplifies retrieval for future features and keeps a snapshot of the score at the time of generation.
