import pandas as pd
import os

# Build the full path to the Excel file using os
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "data", "respuestas.xlsx")


def process_excel(file_name: str, sheet_name: str):
    """
    Loads a sheet from an Excel file into a pandas DataFrame
    and iterates over each record.

    Args:
        file_name (str): Path or name of the Excel file.
        sheet_name (str): Name of the sheet to load.

    Returns:
        str: Generated dataframe
    """

    # Load the sheet as a DataFrame
    df = pd.read_excel(file_name, sheet_name=sheet_name)

    print("DataFrame loaded successfully:")
    print(df.head())  # Show the first rows to verify the content

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        print(f"\nRecord {index}:")
        # Access each column by name
        for column, value in row.items():
            print(f"  {column}: {value}")

    # Return the DataFrame
    return df


if __name__ == "__main__":
    process_excel(file_path, "Respuestas de formulario 1")
