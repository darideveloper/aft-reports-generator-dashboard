# Design: Add Area Field

## Overview
The goal is to extend the participant profile with a "department" field to allow companies to segment survey results by area.

## Data Model
The `Participant` model will be updated with a new `CharField` called `department`. 
The field will use a set of predefined choices to ensure data consistency.

### Schema Changes
- `survey.Participant`: Add `department` (CharField, choices=DEPARTMENT_CHOICES, max_length=255, null=True, blank=True).

## Choice Management
Choices will be stored in `core/choices.py` alongside other participant-related choices (gender, birth range, position).
Initial 5 sample values:
- `hr`: Human Resources
- `it`: IT
- `sales`: Sales
- `marketing`: Marketing
- `finance`: Finance

## API Integration
The `ParticipantDataSerializer` will be updated to include the `department` field. This ensures that when the frontend sends the participant data, the area is validated against the allowed choices and saved to the database.

## Admin Dashboard
The Django admin for `Participant` will be updated to include `department` in the list view and as a filter. This provides immediate visibility and segmentation capabilities for administrators.

## Trade-offs and Considerations
- **Predefined vs. Free Text**: Using predefined choices ensures data quality but requires backend updates to add new areas. For now, sample values are sufficient as per requirements.
- **Optional vs. Required**: The field is **optional** (`null=True`, `blank=True`) to maintain backward compatibility with existing participants and to allow for cases where the area might not be known.
