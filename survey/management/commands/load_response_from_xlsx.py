import pandas as pd
import os
import random
import string

from survey.models import Question, QuestionOption

# Build the full path to the Excel file using os
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "data", "respuestas.xlsx")
sheet_name = "Respuestas de formulario 1"

POSITION_CHOICES = {
    "Director": "director",
    "Gerente": "manager",
    "Supervisor": "supervisor",
    "Operador": "operator",
    "Otro": "other",
}


def process_excel(file_name: str, sheet_name: str) -> pd.DataFrame:
    """
    Loads a sheet from an Excel file into a pandas DataFrame
    and iterates over each record.

    Args:
        file_name (str): Path or name of the Excel file.
        sheet_name (str): Name of the sheet to load.

    Returns:
        df (pd.DataFrame): Generated dataframe
    """

    # Load the sheet as a DataFrame
    df = pd.read_excel(file_name, sheet_name=sheet_name)

    print("DataFrame loaded successfully:")
    print(df.head())  # Show the first rows to verify the content

    # Return the DataFrame
    return df


def generate_random_string(length: int = 10) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def extract_question_option_ids(row) -> list[int]:
    """
    Given a pandas row where:
      - Column names = Question.text
      - Cell values  = QuestionOption.text

    Args:
        row (pandas.Series): A row from a pandas DataFrame.

    Returns:
        List[int]: A list of QuestionOption IDs found in the row.
    """

    option_ids = []

    for column_name, cell_value in row.items():

        # Ignore empty / NaN cells
        if pd.isna(cell_value) or cell_value == "":
            continue

        try:
            # Get the question that matches the column name
            question = Question.objects.get(text=column_name)

            # Get the option that matches the answer in the cell
            option = QuestionOption.objects.get(
                question=question,
                text=str(cell_value).strip()
            )

            option_ids.append(option.id)

        except Question.DoesNotExist:
            print(f"[WARN] No Question found with text='{column_name}'")
        except QuestionOption.DoesNotExist:
            print(
                f"[WARN] No QuestionOption found for question='{column_name}' "
                f"with option='{cell_value}'"
            )

    return option_ids


def get_json_responses(data: pd.DataFrame) -> list[dict]:
    """
    Build json response from data

    Args:
        data (DataFrame): DataFrame containing the data to send.

    Returns:
        list: json_data_list
    """
    json_data_list = []
    # Iterate over each row in the DataFrame
    for index, row in data.iterrows():
        print(f"\nRecord {index}:")
        name = row["Primer nombre y primer apellido"]
        gender = row["Género"].lower()[0]
        birth_date = row["Año de nacimiento"]
        position = POSITION_CHOICES[row["Posición"]]
        email = row["Dirección de correo electrónico"]

        if pd.isna(email) or email == "":
            random_string = generate_random_string()
            email = f"no-email-{random_string}@email.com"

        participant = {
            "name": name,
            "gender": gender,
            "birth_date": birth_date,
            "position": position,
            "email": email,
        }

        answers = extract_question_option_ids(row)

        json_data = {
            "invitation_code": "DariDevAFT2025",
            "survey_id": 1,
            "participant": participant,
            "answers": answers,
        }

        json_data_list.append(json_data)

    return json_data_list


if __name__ == "__main__":
    # Validate if the file exists
    if not os.path.exists(file_path):
        print("Excel file not found")
    else:
        data = process_excel(file_path, sheet_name)
        json_data = get_json_responses(data)
