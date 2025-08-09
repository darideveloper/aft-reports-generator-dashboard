from django.db import models
from django.contrib import admin

from utils.text_generation import get_uuid


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Nombre", unique=True)
    details = models.TextField(
        blank=True,
        null=True,
        verbose_name="Detalles",
        help_text="Detalles adicionales de la empresa. "
        "Información interna, no visible en los reportes",
    )
    logo = models.ImageField(
        upload_to="companies/logos/",
        blank=True,
        null=True,
        verbose_name="Logo",
        help_text="Logo de la empresa. Se mostrará en los reportes",
    )
    invitation_code = models.CharField(
        max_length=255,
        verbose_name="Código de Invitación",
        unique=True,
        default=get_uuid,
        help_text="Código de invitación para acceder a la encuesta."
        "Ejemplo: LeadForwardNissan2025",
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.invitation_code}"

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"


class Survey(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Nombre")
    instructions = models.TextField(
        blank=True,
        null=True,
        verbose_name="Instrucciones",
        help_text="Instrucciones para el participante. "
        "Se mostrarán al inicio de la encuesta.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Encuesta"
        verbose_name_plural = "Encuestas"


class QuestionGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Nombre")
    details = models.TextField(blank=True, null=True, verbose_name="Detalles")
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, verbose_name="Encuesta"
    )
    survey_index = models.IntegerField(
        default=1,
        verbose_name="Posición",
        help_text="Posición del grupo en la encuesta",
    )
    survey_percentage = models.FloatField(
        default=0, verbose_name="Porcentaje", help_text="Porcentaje de la encuesta"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.survey_index}. {self.name}"

    class Meta:
        verbose_name = "Grupo de Preguntas"
        verbose_name_plural = "Grupos de Preguntas"


class Question(models.Model):

    QUESTION_TYPE_CHOICES = [
        ("text", "Texto"),
        ("select", "Selección"),
    ]

    id = models.AutoField(primary_key=True)
    question_group = models.ForeignKey(
        QuestionGroup, on_delete=models.CASCADE, verbose_name="Grupo de Preguntas"
    )
    question_group_index = models.IntegerField(
        default=1,
        verbose_name="Posición",
        help_text="Posición de la pregunta en el grupo",
    )
    question_type = models.CharField(
        max_length=255, choices=QUESTION_TYPE_CHOICES, verbose_name="Tipo de Pregunta"
    )
    text = models.TextField(verbose_name="Pregunta")
    details = models.TextField(
        blank=True, null=True, verbose_name="Detalles adicionales"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        text = f"{self.question_group.survey_index}. "
        text += f"{self.question_group_index}. "
        text += f"{self.text}"
        return text

    class Meta:
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"

    @property
    def survey(self):
        return self.question_group.survey

    @admin.display(description="Encuesta", ordering="question_group__survey__name")
    def get_survey_for_admin(self):
        return self.survey.name


class QuestionOption(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, verbose_name="Pregunta"
    )
    question_index = models.IntegerField(
        default=1,
        verbose_name="Posición",
        help_text="Posición de la opción en la pregunta",
    )
    points = models.IntegerField(
        default=0,
        verbose_name="Puntos",
        help_text="".join(
            [
                "Recomendado: 1 en caso de que sea una respuesta correcta, ",
                "de lo contrario 0",
            ]
        ),
    )
    text = models.TextField(verbose_name="Opción")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        text = f"{self.question.question_group.survey_index}."
        text += f"{self.question.question_group_index}."
        text += f"{self.question.text}"
        text += f" - {self.text}"
        return text

    class Meta:
        verbose_name = "Opción de Pregunta"
        verbose_name_plural = "Opciones de Preguntas"

    @property
    def survey(self):
        return self.question.survey

    @admin.display(description="Encuesta", ordering="survey__name")
    def get_survey_for_admin(self):
        return self.survey.name

    @property
    def question_group(self):
        return self.question.question_group

    @admin.display(description="Grupo de Preguntas", ordering="question_group__name")
    def get_question_group_for_admin(self):
        return self.question_group.name


class Participant(models.Model):

    GENDER_CHOICES = [
        ("m", "Masculino"),
        ("f", "Feminino"),
        ("o", "Otro"),
    ]

    BIRTH_RANGE_CHOICES = [
        ("1946-1964", "1946-1964"),
        ("1965-1980", "1965-1980"),
        ("1981-1996", "1981-1996"),
        ("1997-2012", "1997-2012"),
    ]

    POSITION_CHOICES = [
        ("director", "Director"),
        ("manager", "Gerente"),
        ("supervisor", "Supervisor"),
        ("operator", "Operador"),
        ("other", "Otro"),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Nombre completo")
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    gender = models.CharField(
        max_length=255, choices=GENDER_CHOICES, verbose_name="Género"
    )
    birth_range = models.CharField(
        max_length=255, choices=BIRTH_RANGE_CHOICES, verbose_name="Rango de Edad"
    )
    position = models.CharField(
        max_length=255,
        choices=POSITION_CHOICES,
        verbose_name="Posición",
        help_text="Posición del participante en la empresa",
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name="Empresa"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Participante"
        verbose_name_plural = "Participantes"


class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, verbose_name="Participante"
    )
    question_option = models.ForeignKey(
        QuestionOption,
        on_delete=models.CASCADE,
        verbose_name="Opción seleccionada de Pregunta",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.participant.name} - {self.question_option.text}"

    class Meta:
        verbose_name = "Respuesta"
        verbose_name_plural = "Respuestas"
