# Scoring Logic Spec

## MODIFIED Requirements

### Requirement: Dynamic Text Selection
The system MUST select the PDF summary text based on the highest configured `min_score` that the participant has achieved, rather than using hardcoded score buckets.

#### Scenario: Participant score falls between thresholds
- **Given** the database has `TextPDFSummary` records with `min_score` 0, 50, and 80
- **When** a participant achieves a score of 65
- **Then** the report should include the text corresponding to `min_score` 50 (highest value <= 65)

#### Scenario: Participant score equals a threshold
- **Given** the database has `TextPDFSummary` records with `min_score` 0, 50, and 80
- **When** a participant achieves a score of 80
- **Then** the report should include the text corresponding to `min_score` 80

#### Scenario: Participant score is lower than all thresholds (edge case)
- **Given** the database has `TextPDFSummary` records starting at `min_score` 50
- **When** a participant achieves a score of 20
- **Then** no text might be selected (or a default if 0 is configured) - *Current behavior implies we usually have a fallback, typically 0 or low score config*

### Requirement: Precise Testing
Tests MUST verify the actual score logic rather than relying on assumed buckets matching hardcoded values.

#### Scenario: Test with score 99
- **Given** a participant with a score of exactly 99
- **When** the report is generated
- **Then** it should select the text appropriate for 99 (likely the > 70 or > 80 bracket depending on config), and NOT blindly validate against the 100-score text unless they share the same config.
