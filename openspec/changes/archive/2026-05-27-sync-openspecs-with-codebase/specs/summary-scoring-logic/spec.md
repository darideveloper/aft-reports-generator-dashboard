## MODIFIED Requirements

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
