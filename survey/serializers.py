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


class ParticipantSerializer(serializers.Serializer):
    email = serializers.EmailField()
    survey_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Survey.objects.all()
    )