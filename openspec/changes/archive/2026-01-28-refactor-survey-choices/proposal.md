# Refactor Survey Choices

## Summary
Move `GENDER_CHOICES`, `BIRTH_RANGE_CHOICES`, and `POSITION_CHOICES` from `survey/models.py` to a new shared file `survey/choices.py` and update all references to use this shared source.

## Motivation
Currently, choice definitions are duplicated in `survey/models.py` and partially in `survey/serializers.py` (as hardcoded lists of keys). This violates DRY constraints and makes maintenance error-prone (e.g., adding a new position requires updating multiple files).

## Design Plan
1.  **Shared File**: Create `survey/choices.py` to store the choice tuples.
2.  **Models**: Import choices in `Participant` model.
3.  **Serializers**: Use the keys from the shared choices in `ParticipantDataSerializer` instead of hardcoding lists.
4.  **Management Commands**: Review usage in `load_response_from_xlsx.py` and verify consistency (explicit update if applicable).
