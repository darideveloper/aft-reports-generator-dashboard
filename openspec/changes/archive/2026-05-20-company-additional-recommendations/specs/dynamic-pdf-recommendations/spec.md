# dynamic-pdf-recommendations

## ADDED Requirements

### Requirement: Define custom additional recommendations

The system MUST allow administrators to define custom additional recommendations for each company via a text area.

#### Scenario: Define custom recommendations in admin
- **WHEN** an admin edits a Company in the Django Admin
- **AND** fills in the "Additional Recommendations" text area with multiple lines of text
- **THEN** the data is saved to the database for that company

### Requirement: Parse recommendations for template

The PDF generation view MUST parse the company's additional recommendations into a list of strings, splitting by newline characters, and pass this list to the PDF template.

#### Scenario: Split recommendations by newline
- **WHEN** a company has two lines of text in their additional recommendations
- **THEN** the view processes this into a Python list of two strings
- **AND** includes it in the context data for the group report PDF

### Requirement: Display dynamic recommendations

The group report PDF MUST display the dynamic additional recommendations under the "10. Recomendaciones adicionales" section if they are provided.

#### Scenario: Show recommendations in PDF
- **WHEN** a company has custom recommendations
- **THEN** the generated PDF includes the "10. Recomendaciones adicionales" header followed by the parsed list of recommendations

### Requirement: Hide recommendations section if empty

The group report PDF MUST hide the "10. Recomendaciones adicionales" header and its corresponding list if no recommendations are provided for the company.

#### Scenario: Hide empty recommendations
- **WHEN** a company's `additional_recommendations` field is null or empty
- **THEN** the generated PDF does NOT show the "10. Recomendaciones adicionales" title
- **AND** does NOT show the "No hay recomendaciones adicionales" fallback text

### Requirement: Always show LeadForward message

The "Mensaje de LeadForward Global Solutions MJ" section MUST always be visible in the group report PDF, regardless of whether additional recommendations are provided.

#### Scenario: Persist LeadForward message
- **WHEN** a company has no additional recommendations
- **THEN** the generated PDF successfully hides the recommendations section
- **AND** still displays the LeadForward message section