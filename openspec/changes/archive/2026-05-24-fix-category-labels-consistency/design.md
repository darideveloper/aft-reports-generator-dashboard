## Context

The `update-category-labels` change successfully renamed the `TMA` category and others in the model choices and some logic. However, several peripheral but important areas were missed, leading to a fragmented user experience and potential data integrity issues. Specifically, fixture content still uses outdated terminology, PDF templates have inconsistent capitalization/naming, and a critical Many-to-Many relationship in the `TextPDFSummary` fixture is missing, which breaks the category-level scoring aggregation.

## Goals / Non-Goals

**Goals:**
- **Terminology Unification**: Replace all instances of "medio ambiente" with "Futuro sustentable e inclusivo" (and include "inclusión") in thematic descriptions and feedback paragraphs.
- **Template Synchronization**: Ensure PDF templates use exact strings from the model to avoid mismatched lookups and visual inconsistencies.
- **Fixture Integrity**: Fix the `TextPDFSummary.json` fixture by adding the `question_groups` relationship field and populating it with the correct topic mappings.
- **Documentation Accuracy**: Update project-level documentation and mock data to reflect the final project terminology.

**Non-Goals:**
- Changing category codes (CD, TN, CS, IP, TMA, EDC).
- Altering the mathematical logic for calculating averages.

## Decisions

- **Fixture Content Refinement**: 
  - Update `QuestionGroup.json` (Topic 12) and `TextPDFQuestionGroup.json` (Topic 14) to use a broader description that includes sustainability and inclusion.
- **Relationship Mapping**: Restore the Many-to-Many mapping in `TextPDFSummary.json` using the following associations:
  - **CD (Cultura digital)**: Topics 1, 2 (pks 2, 3)
  - **TN (Tecnología y negocios)**: Topics 3, 9 (pks 4, 11)
  - **CS (Ciberseguridad)**: Topics 5, 7 (pks 7, 9)
  - **IP (Impacto personal)**: Topics 6, 11, 13 (pks 8, 13, 15)
  - **TMA (Futuro sustentable e inclusivo)**: Topics 10, 12 (pks 12, 14)
  - **EDC (Ecosistema digital de colaboración)**: Topics 4, 8 (pks 5, 10)
- **Standardized Labels**: Update `group_report_template.html` to use:
  - "Cultura digital" (instead of "Cultura Digital")
  - "Tecnología y negocios" (instead of "Tecnología y Negocio")
  - "Ciberseguridad" (instead of "Ciberseguridad")
  - "Impacto personal" (instead of "Impacto Personal")
  - "Futuro sustentable e inclusivo" (instead of "Futuro Sustentable e Inclusivo")
  - "Ecosistema digital de colaboración" (instead of "Ecosistema Digital de Colaboración")

## Risks / Trade-offs

- **[Risk]**: Manual mapping in fixtures might be misaligned if PKs change in different environments.
  - **Mitigation**: Use standard PKs from existing fixtures and verify against `QuestionGroup.json`.
- **[Risk]**: Existing DB records might not be updated by loading fixtures if `loaddata` is not run with the correct flags or if manual changes were made in production.
  - **Mitigation**: Instruction to run `python manage.py loaddata` will be included in the tasks.
