# Tasks: Add Department Field

## 1. Preparation
- [x] 1.1 Add `DEPARTMENT_CHOICES` to `core/choices.py`. <!-- id: 1 -->

## 2. Implementation
- [x] 2.1 Add `department` field to `Participant` model in `survey/models.py`. <!-- id: 2 -->
- [x] 2.2 Create and run database migrations. <!-- id: 3 -->
- [x] 2.3 Update `ParticipantDataSerializer` in `survey/serializers.py` to include `department`. <!-- id: 4 -->
- [x] 2.4 Update `ParticipantAdmin` in `survey/admin.py` to include `department` in `list_display` and `list_filter`. <!-- id: 5 -->
- [x] 2.5 Update `OptionsView` in `survey/views.py` to include `department` choices. <!-- id: 10 -->
- [x] 2.6 Update `create_test_responses.py` management command to include `department` in random data. <!-- id: 6 -->

## 3. Verification
- [x] 3.1 Verify that the `department` field appears in the Django admin. <!-- id: 7 -->
- [x] 3.2 Verify that the API accepts the `department` field and saves it correctly. <!-- id: 8 -->
- [x] 3.3 Verify that `create_test_responses` generates participants with the `department` field. <!-- id: 9 -->

