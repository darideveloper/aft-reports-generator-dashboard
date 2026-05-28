## Context

Recently, the OpenSpec and application models were updated to enforce the category name "Futuro sustentable e inclusivo" for the TMA code. However, the business decision has been made to revert this change and use the terminology "Tecnología y medio ambiente". Currently, the AI agent is enforcing the "Futuro sustentable e inclusivo" terminology because of strict rules in the `openspec/` files, leading to bugs in logic like `get_priority_actions` which still expected the old name.

## Goals / Non-Goals

**Goals:**
- Completely revert the terminology "Futuro sustentable e inclusivo" back to "Tecnología y medio ambiente" across all OpenSpec requirements, codebase files, database models, and active database records.
- Ensure the AI agent stops reverting manual fixes by removing the strict `MUST` clauses enforcing the previous terminology.

**Non-Goals:**
- Refactoring the entire calculation logic to stop relying on string matching. This is a targeted change to revert the nomenclature and relax the specification rules.

## Decisions

- **Direct String Replacement**: We will perform a direct search-and-replace for the exact strings across all relevant files (specs, models, templates, utils, tests).
- **Database Update Script**: Instead of creating a complex Django data migration, a one-off script will be run within the Django shell to update existing `QuestionGroup` and `TextPDFQuestionGroup` records to ensure the production database immediately aligns with the new code state.
- **Spec Relaxation**: We will remove the explicit requirements that state the category *MUST* be named "Futuro sustentable e inclusivo" to give developers and product teams more flexibility in the future.

## Risks / Trade-offs

- **[Risk] State mismatch between code and DB** → Mitigation: We will update the database fixtures and run a one-off database update script simultaneously with the code deployment to ensure strings match for `get_priority_actions`.
