# summary-scoring-logic Specification

## Purpose
Define the scoring methodology and mapping for competency category summaries in the PDF report, ensuring consistent ordering and dynamic threshold-based text selection.
## Requirements
### Requirement: Calculate Summary Categories based on Thematic Averages
The system MUST calculate a score for each of the 6 summary categories by averaging the scores of their related topics, and select the summary text where the score is less than or equal to the threshold (`score <= min_score`).

#### Scenario: Participant with mixed scores
- **Given** a participant has completed a survey.
- **And** Topic 1 (Antecedentes) has a score of 80.
- **And** Topic 2 (Evolución) has a score of 60.
- **And** "Cultura digital" (CD) category is mapped to Topics 1 and 2.
- **And** summary levels exist for 100.0, 79.0, and 49.0.
- **When** the summary scores are calculated.
- **Then** the "Cultura digital" category score should be 70.
- **And** the paragraph selected for "Cultura digital" in the PDF should be the one with `min_score = 79.0` (because 70 <= 79).

### Requirement: Persistent Storage of Summary Scores
The system MUST save each calculated average for a summary category in the database for each report.

#### Scenario: Save scores for future audit
- **Given** a report is being generated.
- **When** the calculations are performed.
- **Then** 6 records in `ReportSummaryScore` should be created/updated for that report.
- **And** each record must contain the category code (e.g., 'CD') and the calculated average score.

### Requirement: Admin-Managed Topic Mapping
The system MUST allow the relationship between topics (QuestionGroups) and summary categories (TextPDFSummary) to be manageable via the Django Admin.

#### Scenario: Update mapping
- **Given** an admin user in the Django Dashboard.
- **When** they edit a `TextPDFSummary` record.
- **Then** they should be able to select multiple `QuestionGroup`s to associate with that summary type.

### Requirement: Differentiated Category Results
The system MUST be able to display different summary levels (e.g., "Misión Cumplida" for one category and "En Desarrollo" for another) in the same report based on their respective thematic averages.

#### Scenario: Differentiated scores in the same report
- **Given** Category A is mapped to Topic 1 (Score: 100).
- **And** Category B is mapped to Topic 2 (Score: 20).
- **When** the report is generated.
- **Then** the PDF should show the summary text corresponding to 100% for Category A.
- **And** the summary text corresponding to 20% for Category B.

### Requirement: Robustness with Missing Mappings
If a summary category has no topics mapped to it, the system MUST NOT crash and MUST fall back to a safe default.

#### Scenario: Category without topics
- **Given** a `TextPDFSummary` category has no related `QuestionGroup`s.
- **When** scores are calculated.
- **Then** the category score should default to 0 (or the overall report total as per final design decision).
- **And** the report generation should complete successfully.

### Requirement: Strict Rendering Order
The system MUST render the summary categories in the PDF in the following fixed order and with the following labels:
1. **CD**: Cultura digital
2. **TN**: Tecnología y negocios
3. **CS**: Ciberseguridad
4. **IP**: Impacto personal
5. **TMA**: Futuro sustentable e inclusivo
6. **EDC**: Ecosistema digital de colaboración

#### Scenario: Consistent PDF layout with updated labels
- **Given** resulting summary texts have been calculated for all categories.
- **When** the PDF is generated.
- **Then** the first 4 categories (CD, TN, CS, IP) must appear on page 20 in that specific sequence.
- **AND** the remaining 2 categories (TMA, EDC) must appear on page 21 in that specific sequence.
- **AND** the category TMA MUST be labeled as "Futuro sustentable e inclusivo".
- **AND** the labels MUST match the casing and pluralization defined in the list above.

