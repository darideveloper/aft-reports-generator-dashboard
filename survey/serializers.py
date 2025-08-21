from django.db import transaction

from rest_framework import serializers

from survey import models


class InvitationCodeSerializer(serializers.Serializer):
    invitation_code = serializers.CharField(max_length=255)


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QuestionOption
        fields = ["id", "text", "question_index", "question"]


class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = models.Question
        fields = [
            "id",
            "text",
            "details",
            "options",
            "question_group_index",
            "question_group",
        ]

    def get_options(self, obj):
        return QuestionOptionSerializer(
            obj.questionoption_set.order_by("question_index"), many=True
        ).data


class QuestionGroupSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()
    modifiers = serializers.SerializerMethodField()

    class Meta:
        model = models.QuestionGroup
        fields = [
            "id",
            "name",
            "details",
            "survey_percentage",
            "questions",
            "survey_index",
            "modifiers",
        ]

    def get_modifiers(self, obj):
        return obj.modifiers.values_list("name", flat=True)

    def get_questions(self, obj):
        return QuestionSerializer(
            obj.question_set.order_by("question_group_index"), many=True
        ).data


class SurveyDetailSerializer(serializers.ModelSerializer):
    question_groups = serializers.SerializerMethodField()

    class Meta:
        model = models.Survey
        fields = [
            "id",
            "name",
            "instructions",
            "created_at",
            "updated_at",
            "question_groups",
        ]

    def get_question_groups(self, obj):
        return QuestionGroupSerializer(
            obj.questiongroup_set.order_by("survey_index"), many=True
        ).data


class ReportSerializer(serializers.Serializer):
    survey_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Survey.objects.all(), required=True
    )
    participant_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Participant.objects.all(), required=True
    )


class HasAnswerSerializer(serializers.Serializer):
    email = serializers.EmailField()
    survey_id = serializers.PrimaryKeyRelatedField(queryset=models.Survey.objects.all())


class ParticipantDataSerializer(serializers.Serializer):
    gender = serializers.ChoiceField(choices=["m", "f", "o"])
    birth_range = serializers.ChoiceField(
        choices=["1946-1964", "1965-1980", "1981-1996", "1997-2012"]
    )
    position = serializers.ChoiceField(
        choices=["director", "manager", "supervisor", "operator", "other"]
    )
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()


class AnswerDataSerializer(serializers.Serializer):
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Question.objects.all(), source="question"
    )
    question_option_id = serializers.PrimaryKeyRelatedField(
        queryset=models.QuestionOption.objects.all(), source="question_option"
    )

    def validate(self, data):
        # Validar que la opción pertenezca a la pregunta
        if data["question_option"].question_id != data["question"].id:
            raise serializers.ValidationError(
                "La opción no pertenece a la pregunta especificada."
            )
        return data


class ResponseSerializer(serializers.Serializer):
    invitation_code = serializers.SlugRelatedField(
        queryset=models.Company.objects.filter(is_active=True),
        slug_field="invitation_code",
    )
    survey_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Survey.objects.all(), source="survey"
    )
    participant = ParticipantDataSerializer(source="participant_data")
    answers = serializers.PrimaryKeyRelatedField(
        queryset=models.QuestionOption.objects.all(), many=True, source="answers_data"
    )

    def validate(self, data):
        participant_email = data.get("participant_data", {}).get("email")
        survey = data.get("survey")

        if participant_email and survey:
            if models.Answer.objects.filter(
                participant__email=participant_email,
                question_option__question__question_group__survey=survey,
            ).exists():
                raise serializers.ValidationError(
                    "This participant has already submitted answers for this survey."
                )

        return data

    def create(self, validated_data):

        company = validated_data.pop("invitation_code")
        participant_data = validated_data.pop("participant_data")
        selected_options = validated_data.pop("answers_data")

        with transaction.atomic():
            participant = models.Participant.objects.create(
                company=company, **participant_data
            )
            for option in selected_options:
                models.Answer.objects.create(
                    participant=participant,
                    question_option=option,
                )

        return participant, selected_options
