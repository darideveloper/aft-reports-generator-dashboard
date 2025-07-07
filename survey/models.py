from django.db import models


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to="companies/logos/", blank=True, null=True)
    invitation_code = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.invitation_code}"
    
    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"


class Survey(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Encuesta"
        verbose_name_plural = "Encuestas"


class QuestionGroup(models.Model):
    id = models.AutoField(primary_key=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Grupo de Preguntas"
        verbose_name_plural = "Grupos de Preguntas"


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    question_group = models.ForeignKey(QuestionGroup, on_delete=models.CASCADE)
    text = models.TextField()
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"


class QuestionOption(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Opción de Pregunta"
        verbose_name_plural = "Opciones de Preguntas"


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
        ("directir", "Director"),
        ("manager", "Gerente"),
        ("supervisor", "Supervisor"),
        ("operator", "Operador"),
        ("other", "Otro"),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=255)
    birth_range = models.CharField(max_length=255, choices=BIRTH_RANGE_CHOICES)
    position = models.CharField(max_length=255, choices=POSITION_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Participante"
        verbose_name_plural = "Participantes"
        
        
class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    question_option = models.ForeignKey(QuestionOption, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.participant.name} - {self.question_option.text}"
    
    class Meta:
        verbose_name = "Respuesta"
        verbose_name_plural = "Respuestas"