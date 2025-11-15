import os
import pandas as pd
import random
import string
from thefuzz import fuzz, process

from django.core.management.base import BaseCommand, CommandError
from survey.models import Question, QuestionOption


POSITION_CHOICES = {
    "Director": "director",
    "Gerente": "manager",
    "Supervisor": "supervisor",
    "Operador": "operator",
    "Otro": "other",
}


class Command(BaseCommand):
    help = (
        "Imports survey responses from Excel and converts them into JSON-like objects."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--invitation",
            type=str,
            required=True,
            help="Invitation code for all responses",
        )
        parser.add_argument(
            "--excel",
            type=str,
            default="respuestas.xlsx",
            help="Excel filename inside the 'data' folder",
        )
        parser.add_argument(
            "--sheet",
            type=str,
            default="Respuestas de formulario 1",
            help="Sheet name to load from Excel",
        )

    def handle(self, *args, **options):

        invitation_code = options["invitation"]
        excel_filename = options["excel"]
        sheet_name = options["sheet"]

        # Build path to /data/<file>
        base_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = os.path.dirname(os.path.dirname(base_dir))
        management_dir = os.path.join(app_dir, "management")
        commands_dir = os.path.join(management_dir, "commands")
        data_dir = os.path.join(commands_dir, "data")
        file_path = os.path.join(data_dir, excel_filename)

        if not os.path.exists(file_path):
            raise CommandError(f"Excel file not found at: {file_path}")

        df = self.process_excel(file_path, sheet_name)
        json_payload = self.get_json_responses(df, invitation_code)

        self.stdout.write(self.style.SUCCESS("JSON payload created successfully"))
        """ for entry in json_payload:
            print(entry) """

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
                question_k = "k) Los líderes pueden tomar mejores decisiones de inversión al distinguir entre la infraestructura (\_\_\_\_\_\_\_) que respalda las funciones organizacionales a largo plazo y la presencia en línea más visible (\_\_\_\_\_\_) que influye en la marca y la participación del cliente."

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
            result = self.get_best_matching_option(
                question_k_id, combined_value
            )

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
            gender = row["Género"].lower()[0]
            birth_date = row["Año de nacimiento"]
            position = POSITION_CHOICES[row["Posición"]]
            email = row["Dirección de correo electrónico"]

            if pd.isna(email) or email == "":
                email = f"no-email-{self.generate_random_string()}@email.com"

            participant = {
                "name": name,
                "gender": gender,
                "birth_date": birth_date,
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
