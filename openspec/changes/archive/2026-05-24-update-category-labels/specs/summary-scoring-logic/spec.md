## MODIFIED Requirements

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
- **And** the remaining 2 categories (TMA, EDC) must appear on page 21 in that specific sequence.
- **And** the category TMA MUST be labeled as "Futuro sustentable e inclusivo".
