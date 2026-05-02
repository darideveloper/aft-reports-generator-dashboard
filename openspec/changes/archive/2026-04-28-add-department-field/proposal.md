# Proposal: Add Department Field

## Why
Currently, the participant registration only captures email, name, sex, and job position. There is a need to also capture the "department" or "area" of the participant (e.g., Human Resources, IT, Sales) for better data segmentation and reporting.

## What Changes
1.  **Choice Data**: Add `DEPARTMENT_CHOICES` to `core/choices.py` with 5 sample values.
2.  **Model Change**: Add a `department` field to the `Participant` model in `survey/models.py`.
3.  **API/Serializer**: Update `ParticipantDataSerializer` in `survey/serializers.py` to include the `department` field.
4.  **Admin Dashboard**: Update `ParticipantAdmin` in `survey/admin.py` to display and filter by the new field.
5.  **Test Data**: Update `create_test_responses` management command to generate data for the new field.

## Impact
- **Affected code**: `core/choices.py`, `survey/models.py`, `survey/serializers.py`, `survey/admin.py`, `survey/management/commands/create_test_responses.py`.
- **New capability**: `department-field`.
