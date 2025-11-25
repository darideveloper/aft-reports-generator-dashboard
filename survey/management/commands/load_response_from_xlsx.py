import os
import json
import requests
import random
import string
import pandas as pd
from thefuzz import fuzz, process

from survey import models
from rest_framework.authtoken.models import Token

from django.core.management.base import BaseCommand, CommandError
from survey.models import Question, QuestionOption


POSITION_CHOICES = {
    "Director": "director",
    "Gerente": "manager",
    "Supervisor": "supervisor",
    "Operador": "operator",
    "Otro": "other",
}

GENDER_CHOICES = {
    "hombre": "m",
    "mujer": "f",
    "otro": "o",
}


class Command(BaseCommand):
    help = (
        "Imports survey responses from Excel and converts them into JSON-like objects."
    )

    # Esxcel path
    EXCEL_PATH = os.path.join(os.path.dirname(__file__), "files", "responses.xlsx")
    SHEET_NAME = "Respuestas de formulario 1"

    # Get invitation code of "Prueba Beta" from db
    INVITATION_CODE = models.Company.objects.get(name="Prueba Beta").invitation_code

    # Get DRF token from db
    TOKEN = Token.objects.order_by("?").first().key

    # Raise error if file does not exist
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"Excel file not found at: {EXCEL_PATH}")

    def handle(self, *args, **options):

        # Build path to /data/<file>
        base_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = os.path.dirname(os.path.dirname(base_dir))
        management_dir = os.path.join(app_dir, "management")
        commands_dir = os.path.join(management_dir, "commands")
        data_dir = os.path.join(commands_dir, "data")
        file_path = os.path.join(data_dir, self.EXCEL_PATH)

        if not os.path.exists(file_path):
            raise CommandError(f"Excel file not found at: {file_path}")

        df = self.process_excel(file_path, self.SHEET_NAME)
        json_payload = self.get_json_responses(df, self.INVITATION_CODE)

        self.stdout.write(self.style.SUCCESS("JSON payload created successfully"))

        self.stdout.write(self.style.SUCCESS("Sending data to API..."))
        self.send_responses_to_api(json_payload, self.TOKEN)

    # --------------------------------------------------------------------------

    def process_excel(self, file_path: str, sheet_name: str) -> pd.DataFrame:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        self.stdout.write(self.style.SUCCESS("Excel loaded successfully"))
        return df

    # --------------------------------------------------------------------------

    def generate_random_string(self, length: int = 10) -> str:
        chars = string.ascii_letters + string.digits
        return "".join(random.choice(chars) for _ in range(length))

    # --------------------------------------------------------------------------

    def get_best_matching_question(self, column_name: str, threshold: int = 65):
        """
        Returns the best matching Question based on fuzzy string similarity.
        """

        if column_name is None or pd.isna(column_name):
            return None

        # Force clean string
        column_name = str(column_name).strip()

        all_questions = list(Question.objects.values_list("text", flat=True))

        # thefuzz requires all strings
        all_questions = [str(q) for q in all_questions]

        result = process.extractOne(column_name, all_questions, scorer=fuzz.ratio)

        if result is None:
            return None

        best_match, score = result

        if score >= threshold:
            return Question.objects.get(text=best_match)

        return None

    def get_best_matching_option(self, question, option_text: str, threshold: int = 65):
        """
        Returns the best matching QuestionOption for a given Question
        based on fuzzy similarity.
        """

        if option_text is None or pd.isna(option_text):
            return None

        option_text = str(option_text).strip()

        # Get all option texts for this question
        all_options = list(
            QuestionOption.objects.filter(question=question).values_list(
                "text", flat=True
            )
        )

        all_options = [str(opt) for opt in all_options]

        # Find best match
        result = process.extractOne(option_text, all_options, scorer=fuzz.ratio)

        if result is None:
            return None

        best_match, score = result

        if score >= threshold:
            return QuestionOption.objects.get(question=question, text=best_match)

        return None

    # --------------------------------------------------------------------------

    def extract_question_option_ids(self, row) -> list[int]:

        option_ids = []
        special_k_values = []  # Collect values for question K

        for column_name, cell_value in row.items():

            if pd.isna(cell_value) or cell_value == "":
                continue

            try:
                # --- Manual normalization rules ---
                target = "Opta por dispositivos de bajo"
                if target in column_name:
                    column_name = "Opta por dispositivos de bajo consumo de energía"

                target = "Apaga los dispositivos cuando"
                if target in column_name:
                    column_name = "Apaga los dispositivos cuando no los uses"

                target = "Usa el almacenamiento en la"
                if target in column_name:
                    column_name = (
                        "Usa el almacenamiento en la nube de manera responsable"
                    )

                target = "Recicle los aparatos electrón"
                if target in column_name:
                    column_name = "Recicle los aparatos electrónicos"

                target = "Elija energías renovables"
                if target in column_name:
                    column_name = "Elija energías renovables"

                target = "Repare, no sustituya"
                if target in column_name:
                    column_name = "Repare, no sustituya"

                target = "Reduzca el uso de papel"
                if target in column_name:
                    column_name = "Reduzca el uso de papel"

                target = "Apoya a las marcas sostenible"
                if target in column_name:
                    column_name = "Apoya a las marcas sostenibles"

                # Find the best matching question
                question = self.get_best_matching_question(str(column_name))

                if question is None:
                    self.stdout.write(
                        self.style.WARNING(
                            f"No Question matched for column '{column_name}'"
                        )
                    )
                    continue

                # --- SPECIAL CASE: question K has two columns ---
                question_k = (
                    "k) Los líderes pueden tomar mejores decisiones de inversión al distinguir "
                    + r"entre la infraestructura (\_\_\_\_\_\_\_) "
                    + "que respalda las funciones organizacionales a largo plazo "
                    + r"y la presencia en línea más visible (\_\_\_\_\_\_) "
                    + "que influye en la marca "
                    + "y la participación del cliente."
                )
                cell_value = str(cell_value).strip()
                if cell_value == "False":
                    cell_value = "Falso"
                elif cell_value == "True":
                    cell_value = "Verdadero"

                if question.text == question_k:
                    # Store the values to combine later
                    special_k_values.append(cell_value)
                    question_k_id = question.id
                    continue  # Don't process yet

                # Normal case: look up the option directly
                option = QuestionOption.objects.get(
                    question=question,
                    text=cell_value,
                )
                option_ids.append(option.id)

            except Question.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"No Question found with text='{column_name}'")
                )
            except QuestionOption.DoesNotExist:
                warning = f"No QuestionOption found for question='{column_name}'"
                warning += f" with option='{cell_value}'"
                self.stdout.write(self.style.WARNING(warning))

        # --- After the loop: process special K question ---
        if special_k_values:
            combined_value = ", ".join(special_k_values)
            result = self.get_best_matching_option(question_k_id, combined_value)

            try:
                option = QuestionOption.objects.get(
                    question__text=question_k, text=result.text
                )
                option_ids.append(option.id)

            except QuestionOption.DoesNotExist:
                warning = "No QuestionOption found for special question K"
                warning += f" with value='{combined_value}'"
                self.stdout.write(self.style.WARNING(warning))
        print(len(option_ids))
        return option_ids

    # --------------------------------------------------------------------------

    def get_json_responses(self, df: pd.DataFrame, invitation_code: str) -> list[dict]:

        json_list = []

        for index, row in df.iterrows():
            print(f"\nProcessing row {index}")

            name = row["Primer nombre y primer apellido"]
            gender = GENDER_CHOICES[row["Género"].lower()]
            birth_date = row["Año de nacimiento"]
            position = POSITION_CHOICES[row["Posición"]]
            email = row["Dirección de correo electrónico"]

            if pd.isna(email) or email == "":
                email = f"no-email-{self.generate_random_string()}@email.com"

            participant = {
                "name": name,
                "gender": gender,
                "birth_range": birth_date,
                "position": position,
                "email": email,
            }

            answers = self.extract_question_option_ids(row)

            json_list.append(
                {
                    "invitation_code": invitation_code,
                    "survey_id": 1,
                    "participant": participant,
                    "answers": answers,
                }
            )

        return json_list

    # --------------------------------------------------------------------------

    def send_responses_to_api(self, payload: list[dict], token: str) -> list:
        """
        Sends a list of survey response dictionaries to the API endpoint.

        Args:
            payload (list[dict]): The JSON-ready list of responses you generated.
            token (str): The authentication token for the API.

        Returns:
            list: A list of results containing status and server replies.
        """

        url = "http://127.0.0.1:8000/api/response/"

        headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json",
        }

        results = []

        for entry in payload:
            try:
                print(entry)
                response = requests.post(
                    url,
                    headers=headers,
                    data=json.dumps(entry),
                    timeout=10,
                )

                results.append(
                    {
                        "sent": entry,
                        "status_code": response.status_code,
                        "response": response.json() if response.content else None,
                    }
                )

                if response.status_code == 201:
                    response_message = f"Data for {entry['participant']['email']}"
                    self.stdout.write(
                        self.style.SUCCESS(response_message + " sent successfully")
                    )
                else:
                    response_message = f"Data for {entry['participant']['email']}"
                    self.stdout.write(
                        self.style.ERROR(
                            response_message
                            + " failed to send with status code: "
                            + str(response.status_code)
                        )
                    )
            except Exception as e:
                results.append(
                    {
                        "sent": entry,
                        "error": str(e),
                    }
                )

        return results
