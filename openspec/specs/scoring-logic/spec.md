# scoring-logic Specification

## Purpose
TBD - created by archiving change fix-pdf-summary-scoring-logic. Update Purpose after archive.
## Requirements
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

#### Scenario: Participant score is below the next threshold (e.g. 69)
- **Given** a participant score of 69
- **And** thresholds defined at 50, 70, and 100
- **When** the test calculates the expected `min_score`
- **Then** it should expect the text associated with `min_score=50` (the highest threshold $\le$ score)

#### Scenario: Participant score is just below 100 (e.g. 99)
- **Given** a participant with a score of exactly 99
- **And** thresholds defined at 50, 70, and 100
- **When** the test calculates the expected `min_score`
- **Then** it should expect the text associated with `min_score=70` (the highest threshold $\le$ score), and NOT blindly validate against the 100-score text.

