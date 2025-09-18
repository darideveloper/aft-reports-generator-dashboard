import os
import uuid

import matplotlib
import numpy as np
import matplotlib.pyplot as plt

from django.conf import settings
from scipy.stats import norm

matplotlib.use("Agg")


def generate_bell_curve_plot(
    grade: str,
    mean_grades: str,
    grades: np.array,
    file_name: str = "grafico_campana.png",
    company_average_total: float = 0,
):
    """Generate bell curve plot

    Args:
        grade (str): applicant's score
        mean_grades (str): score's mean
        grades (str): applicants score list data
        file_name (str): plot image file's name
        company_average_total (float): global company average

    Returns:
        str: Generated path plot
    """
    # Calculate empiric parameters
    mu = np.mean(grades)
    sigma = np.std(grades)

    # Create adjusted normal distribution
    x = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 1000)
    y = norm.pdf(x, mu, sigma)

    # Create figure
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, color="#3366cc", linewidth=2.5, label="Distribución General")

    # Lines of interest
    plt.axvline(
        x=company_average_total,
        color="#ff9900",
        linestyle="--",
        linewidth=2,
        label=f"Media de grupo ({company_average_total})",
    )
    plt.axvline(
        x=grade,
        color="#cc0000",
        linestyle="--",
        linewidth=2,
        label=f"Participante ({grade})",
    )
    plt.axvline(
        x=mean_grades,
        color="#7465BF",
        linestyle="--",
        linewidth=2,
        label=f"Media Global ({mean_grades})",
    )

    # Fill area under the curve
    x_fill = x[x <= grade]
    y_fill = norm.pdf(x_fill, mu, sigma)
    plt.fill_between(x_fill, y_fill, color="#cc0000", alpha=0.2)

    plt.title(
        "Distribución de Resultados - Posición del Participante",
        fontsize=16,
        fontweight="bold",
    )
    plt.xlabel("Índice de Resultado", fontsize=12)
    plt.ylabel("Densidad Poblacional", fontsize=12)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.legend(frameon=False, fontsize=11)

    plt.grid(False)
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    plt.gca().set_facecolor("white")
    plt.tight_layout()

    # Create folder in case it doesn't exists
    carpeta_salida = os.path.join(settings.BASE_DIR, "media", "temp")
    os.makedirs(carpeta_salida, exist_ok=True)

    # Save plot
    ruta_salida = os.path.join(carpeta_salida, file_name)
    plt.savefig(ruta_salida, dpi=300)
    plt.close()

    # Return absolut path
    return os.path.abspath(ruta_salida)


if __name__ == "__main__":
    np.random.seed(0)
    datos = np.random.normal(70, 10, 1000)

    # Generate plot
    ruta = generate_bell_curve_plot(
        grade=65,
        mean_grades=70,
        grades=datos,
        file_name=f"graico-{uuid.uuid4()}.png",
    )
    print("Image save at:", ruta)
