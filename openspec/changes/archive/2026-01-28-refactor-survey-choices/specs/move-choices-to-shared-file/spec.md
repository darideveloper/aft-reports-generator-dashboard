# Refactor Survey Choices

## ADDED Requirements

### Requirement: Centralized Choice Definitions
The application MUST implicitly store `GENDER_CHOICES`, `BIRTH_RANGE_CHOICES`, and `POSITION_CHOICES` in a single location to ensure consistency across models and serializers.

#### Scenario: Verify choices file
Given the file `survey/choices.py` exists
Then it should contain `GENDER_CHOICES`
And it should contain `BIRTH_RANGE_CHOICES`
And it should contain `POSITION_CHOICES`

#### Scenario: Verify Model Usage
Given `survey/models.py`
Then `Participant` model should import `GENDER_CHOICES` from `.choices`
And `Participant` model should import `BIRTH_RANGE_CHOICES` from `.choices`
And `Participant` model should import `POSITION_CHOICES` from `.choices`

#### Scenario: Verify Serializer Usage
Given `survey/serializers.py`
Then `ParticipantDataSerializer` fields should use keys derived from the imported choices in `survey/choices.py`
