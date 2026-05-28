## MODIFIED Requirements

### Requirement: Consistent Labeling and Casing
The system SHALL ensure that all category labels rendered in the PDF report exactly match the labels defined in the `survey.models.TextPDFSummary.TEXT_TYPE_CHOICES` in terms of spelling, casing, and pluralization.

#### Scenario: PDF Label Casing Verification
- **WHEN** the PDF is generated
- **THEN** the labels for "Cultura digital", "Tecnología y negocios", "Ciberseguridad", "Impacto personal", "Tecnología y medio ambiente", and "Ecosistema digital de colaboración" MUST be rendered in lowercase (except for the first letter) exactly as defined in the model choices.
