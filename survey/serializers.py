from rest_framework import serializers

from .models import Company, Survey, QuestionGroup, Question, QuestionOption


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class InvitationCodeSerializer(serializers.Serializer):
    invitation_code = serializers.CharField(max_length=255)


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ["id", "text"]


class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["id", "text", "details", "options"]

    def get_options(self, obj):
        return QuestionOptionSerializer(
            obj.questionoption_set.order_by("question_index"), many=True
        ).data


class QuestionGroupSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = QuestionGroup
        fields = ["id", "name", "details", "survey_percentage", "questions"]

    def get_questions(self, obj):
        return QuestionSerializer(
            obj.question_set.order_by("question_group_index"), many=True
        ).data


class SurveyDetailSerializer(serializers.ModelSerializer):
    question_groups = serializers.SerializerMethodField()

    class Meta:
        model = Survey
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
