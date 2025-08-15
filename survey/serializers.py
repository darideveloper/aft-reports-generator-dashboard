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

    class Meta:
        model = models.QuestionGroup
        fields = [
            "id",
            "name",
            "details",
            "survey_percentage",
            "questions",
            "survey_index",
        ]

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
    survey_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Survey.objects.all()
    )

    def validate(self, data):
        email = data["email"]
        survey = data["survey_id"]

        has_answer = models.Answer.objects.filter(
            participant__email=email,
            question_option__question__question_group__survey=survey
        ).exists()

        if not has_answer:
            raise serializers.ValidationError(
                {"has_answer": "El participante no tiene respuestas para esta encuesta."}
            )

        # Podemos incluirlo para que el view lo tenga listo
        data["has_answer"] = True
        return data


class ParticipantDataSerializer(serializers.Serializer):
    gender = serializers.ChoiceField(choices=["m", "f", "o"])
    birth_range = serializers.ChoiceField(choices=[
        "1946-1964", "1965-1980", "1981-1996", "1997-2012"
    ])
    position = serializers.ChoiceField(choices=[
        "director", "manager", "supervisor", "operator", "other"
    ])
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()


class AnswerDataSerializer(serializers.Serializer):
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Question.objects.all(),
        source="question"
    )
    question_option_id = serializers.PrimaryKeyRelatedField(
        queryset=models.QuestionOption.objects.all(),
        source="question_option"
    )

    def validate(self, data):
        # Validar que la opción pertenezca a la pregunta
        if data["question_option"].question_id != data["question"].id:
            raise serializers.ValidationError(
                "La opción no pertenece a la pregunta especificada."
            )
        return data


class ResponseSerializer(serializers.Serializer):
    invitation_code = serializers.CharField(max_length=255)
    survey_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Survey.objects.all(),
        source="survey"
    )
    participant = ParticipantDataSerializer(source="participant_data")
    answers = AnswerDataSerializer(many=True, source="answers_data")

    def validate_invitation_code(self, value):
        try:
            company = models.Company.objects.get(invitation_code=value)
        except models.Company.DoesNotExist:
            raise serializers.ValidationError("El código de invitación no es válido.")
        # Guardamos la instancia para usarla luego en validated_data
        self.company = company
        return value

    def validate(self, data):
        # Inyectar company validada para usar en la vista
        data["company"] = getattr(self, "company", None)

        survey = data["survey"]                        # Survey (instancia)
        p = data.get("participant_data", {})
        email = p.get("email")

        # Validar si YA respondió este survey
        already_answered = models.Answer.objects.filter(
            participant__email=email,
            question_option__question__question_group__survey=survey
        ).exists()

        if already_answered:
            raise serializers.ValidationError(
                {"participant": "No puede volver a hacer este cuestionario."}
            )

        return data