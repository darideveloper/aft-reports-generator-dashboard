# Spec Delta: Test Logic Correction

## MODIFIED Requirements

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
