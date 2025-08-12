from csv import Dialect
import os
import io
import json
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import legal
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color
import numpy as np
from graphics_generator import generate_bell_curve_plot


current_folder = os.path.dirname(__file__)
parent_folder = os.path.dirname(current_folder)
files_folder = os.path.join(parent_folder, "files")

# Create files folder in case it doesn't exist
os.makedirs(files_folder, exist_ok=True)

templates_folder = os.path.join(current_folder, "pdf_utils")
original_pdf = os.path.join(templates_folder, "template.pdf")
logo_path = os.path.join(templates_folder, "logo.png")
graph_path = os.path.join(templates_folder, "logo.png")
fonts_folder = os.path.join(templates_folder, "fonts")
arial = os.path.join(fonts_folder, "ARIAL.TTF")
arial_bold = os.path.join(fonts_folder, "ARIALBD.TTF")

# Open JSON with mockup data
with open("mock_up_scores.json", 'r', encoding='utf-8') as f:
    mock_up_data = json.load(f)

with open("mock_up_results.json", 'r', encoding='utf-8') as f:
    mock_up_results = json.load(f)


def footer_setting(c: canvas.Canvas, name: str, width: float, color: Color):
    """Draw centered footer content

    Args:
        c (canvas.Canvas): PDF Canvas representation
        name (str): applicant's name
        width (float): PDF page width
        color (Color): RGB color to draw text
    """
    footer_text = f"Reporte AFT de {name}"
    text_width = c.stringWidth(footer_text, "arial", 9)
    x = (width - text_width) / 2 + 15
    c.setFont("arial", 9)
    c.setFillColor(color)  # we could also use Color(0.7, 0.7, 0.7)
    c.drawString(x, 53, footer_text)


def justify_text(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float = 467,
    font: str = "arial",
    font_size: float = 11,
):
    """Justify text on PDF file

    Args:
        c (canvas.Canvas): PDF Canvas representation
        text (str): text to justify
        x (float): x coordinate
        y (float): y coordinate
        width (float): PDF page width
        font (str): font name
        font_size (int): font size
    """
    c.setFont(font, font_size)

    words = text.split(" ")
    line = []
    line_width = 0
    space_width = c.stringWidth(" ", font, font_size)

    lines = []  # Store formated lines

    for word in words:
        word_width = c.stringWidth(word, font, font_size)

        if line_width + word_width <= width:
            line.append(word)
            line_width += word_width + space_width
        else:
            lines.append(line)
            line = [word]
            line_width = word_width + space_width

    if line:
        lines.append(line)

    for i, line in enumerate(lines):
        final = i == len(lines) - 1
        draw_justified_line(c, line, x, y, width, font, font_size, final)
        y -= font_size + 4


def draw_justified_line(c, words, x, y, width, font, font_size, final):
    """Draw a line with justification

    Args:
        c (canvas.Canvas): PDF Canvas representation
        words (list): list of words
        x (float): x coordinate
        y (float): y coordinate
        width (float): PDF page width
        font (str): font name
        font_size (int): font size
        final (bool): if it's the last line
    """
    total_spaces = len(words) - 1
    text_width = sum(c.stringWidth(word, font, font_size) for word in words)

    if total_spaces > 0:
        extra_space = (width - text_width) / total_spaces
    else:
        extra_space = 0

    if final:
        extra_space = 4

    current_x = x
    for word in words:
        c.drawString(current_x, y, word)
        current_x += c.stringWidth(word, font, font_size) + extra_space


def generate_report(
    name: str,
    date: str,
    grade_code: str,
    final_score: float,
    logo_path: str,
    graph_path: str,
    data: list,
    resulting_paragraphs: list,
    resulting_titles: Dialect,
) -> str:
    """Generate PDF report from data

    Args:
        name (str): applicant's name
        date (str): report issue date
        grade_code (str): acronym for rating-based description
        final_score (str): applicant's final score
        logo_path (str): path to business logo
        graph_path (str): path to scores path
        data (list): applicants scores list
        resulting_paragraphs (list): list of score and paragraph dicts
        resulting_titles (dict): dict of subtitles and paragraphs for final section

    Returns:
        str: Generated path file
    """

    def footer_setting(c: canvas.Canvas, name: str, width: float, color: Color):
        """Draw centered footer content

        Args:
            c (canvas.Canvas): PDF Canvas representation
            name (str): applicant's name
            width (float): PDF page width
            color (Color): RGB color to draw text
        """
        footer_text = f"Reporte AFT de {name}"
        text_width = c.stringWidth(footer_text, "arial", 9)
        x = (width - text_width) / 2 + 15
        c.setFont("arial", 9)
        c.setFillColor(color)  # we could also use Color(0.7, 0.7, 0.7)
        c.drawString(x, 53, footer_text)

    packet = io.BytesIO()
    # Fonts with epecific path
    pdfmetrics.registerFont(TTFont("arial", arial))
    pdfmetrics.registerFont(TTFont("arialbd", arial_bold))

    c = canvas.Canvas(packet, legal)

    width, height = legal
    color_darkgrey = Color(153 / 255, 153 / 255, 153 / 255)

    # Page 1
    c.setFont("arialbd", 22)
    c.drawRightString(width - 70, 300, name)
    c.drawRightString(width - 70, 270, date)

    image_width = 130
    x = (width - image_width) / 2
    c.drawImage(logo_path, x, 115, width=image_width, height=image_width)

    # Draw footer content
    footer_setting(c, name, width, color_darkgrey)

    c.showPage()

    # Page 2
    # Draw footer content
    footer_setting(c, name, width, color_darkgrey)

    c.showPage()

    # Page 3
    c.setFont("arialbd", 11)
    c.drawString(73, 675, f'"{name}".')

    data = np.array(data)

    bell_plot_path = generate_bell_curve_plot(final_score, data.mean(), data)
    image_width = 400
    x = (width - image_width) / 2
    c.drawImage(bell_plot_path, x, 390, width=image_width, height=200)

    c.setFont("arialbd", 30)
    c.drawString(68, 328, "□")

    c.setFont("arialbd", 30)
    c.drawString(68, 295, "□")

    c.setFont("arialbd", 30)
    c.drawString(68, 263, "□")

    c.setFont("arialbd", 30)
    c.drawString(68, 231, "□")

    c.setFont("arialbd", 30)
    c.drawString(68, 200, "□")

    if grade_code == "MDP":
        c.setFont("arialbd", 30)
        c.drawString(68, 328, "■")
    elif grade_code == "DP":
        c.setFont("arialbd", 30)
        c.drawString(68, 295, "■")
    elif grade_code == "P":
        c.setFont("arialbd", 30)
        c.drawString(68, 263, "■")
    elif grade_code == "AP":
        c.setFont("arialbd", 30)
        c.drawString(68, 231, "■")
    elif grade_code == "MEP":
        c.setFont("arialbd", 30)
        c.drawString(68, 200, "■")

    c.setFont("arialbd", 11)
    c.drawString(275, 150, f'"{name}".')

    # Draw footer content
    footer_setting(c, name, width, color_darkgrey)

    c.showPage()

    # Page 6
    c.setFont("arialbd", 14)
    c.drawString(215, 707, f'"{name}"')

    image_width = width - 140
    x = (width - image_width) / 2
    c.drawImage(graph_path, x, 320, width=image_width, height=image_width - 100)

    # Draw footer content
    footer_setting(c, name, width, color_darkgrey)

    c.showPage()

    # Pages 7 - 19
    for i in range(13):
        score = resulting_paragraphs[i]["score"]
        c.setFont("arialbd", 12)
        c.drawString(69, 660, f" Calificación {score}%")

        text = resulting_paragraphs[i]["text"]
        justify_text(c, text, x=72, y=520)

        # Draw footer content
        footer_setting(c, name, width, color_darkgrey)

        c.showPage()
    
    # Page 4
    # Draw footer content
    footer_setting(c, name, width, color_darkgrey)

    c.showPage()

    # Page 5
    # Draw footer content
    footer_setting(c, name, width, color_darkgrey)

    c.showPage()

    # Page 20
    title_y = 642
    title_x = 97
    paragraph_y = 620
    paragraph_x = 72

    for element in list(resulting_titles.keys())[:4]:
        c.setFont("arialbd", 14)
        c.drawString(title_x, title_y, f"{resulting_titles[element]['subtitle']}")
        text = resulting_titles[element]['paragraph']
        justify_text(c, text, x=paragraph_x, y=paragraph_y)
        title_y -= 145
        paragraph_y -= 145

    # Draw footer content
    footer_setting(c, name, width, color_darkgrey)

    c.showPage()

    # Page 21
    title_y = 660
    title_x = 97
    paragraph_y = 638
    paragraph_x = 72

    for element in list(resulting_titles.keys())[4:6]:
        c.setFont("arialbd", 14)
        c.drawString(title_x, title_y, f"{resulting_titles[element]['subtitle']}")
        text = resulting_titles[element]['paragraph']
        justify_text(c, text, x=paragraph_x, y=paragraph_y)
        title_y -= 161
        paragraph_y -= 161

    # Draw footer content
    footer_setting(c, name, width, color_darkgrey)

    c.showPage()

    c.save()

    packet.seek(0)

    new_pdf = PdfReader(packet)

    existing_pdf = PdfReader(open(original_pdf, "rb"))
    output = PdfWriter()

    # Pages creation
    for i in range(21):
        page = existing_pdf.pages[i]
        page.merge_page(new_pdf.pages[i])
        output.add_page(page)

    new_pdf = os.path.join(files_folder, f"{name}.pdf")
    output_stream = open(new_pdf, "wb")
    output.write(output_stream)
    output_stream.close()
    print(f"File {name} generated correctly")

    return new_pdf


if __name__ == "__main__":
    generate_report(
        name="Abel Soto",
        date="30/12/2025",
        grade_code="MDP",
        final_score=38.9,
        logo_path=logo_path,
        graph_path=graph_path,
        data=np.array(
            [
                53.1,
                48.7,
                61.5,
                55.0,
                42.3,
                67.8,
                50.2,
                59.1,
                45.4,
                62.7,
                38.9,
                56.6,
                47.3,
                64.0,
                51.9,
                44.7,
                58.4,
                49.0,
                54.8,
                40.5,
            ]
        ),
        resulting_paragraphs=mock_up_data,
        resulting_titles=mock_up_results,
    )

    generate_report(
        name="Abel Soto Martinez",
        date="30/12/2025",
        grade_code="P",
        final_score=50,
        logo_path=logo_path,
        graph_path=graph_path,
        data=np.array(
            [
                53.1,
                48.7,
                61.5,
                55.0,
                42.3,
                67.8,
                50.2,
                59.1,
                45.4,
                62.7,
                38.9,
                56.6,
                47.3,
                64.0,
                51.9,
                44.7,
                58.4,
                49.0,
                54.8,
                40.5,
            ]
        ),
        resulting_paragraphs=mock_up_data,
        resulting_titles=mock_up_results,
    )

    generate_report(
        name="Abel Soto Martinez de la Cruz Parez de Dios",
        date="30/12/2025",
        grade_code="MEP",
        final_score=70,
        logo_path=logo_path,
        graph_path=graph_path,
        data=np.array(
            [
                53.1,
                48.7,
                61.5,
                55.0,
                42.3,
                67.8,
                50.2,
                59.1,
                45.4,
                62.7,
                38.9,
                56.6,
                47.3,
                64.0,
                51.9,
                44.7,
                58.4,
                49.0,
                54.8,
                40.5,
            ]
        ),
        resulting_paragraphs=mock_up_data,
        resulting_titles=mock_up_results,
    )

    generate_report(
        name="Sample",
        date="30/12/2025",
        grade_code="MEP",
        final_score=70,
        logo_path=logo_path,
        graph_path=graph_path,
        data=np.array(
            [
                53.1,
                48.7,
                61.5,
                55.0,
                42.3,
                67.8,
                50.2,
                59.1,
                45.4,
                62.7,
                38.9,
                56.6,
                47.3,
                64.0,
                51.9,
                44.7,
                58.4,
                49.0,
                54.8,
                40.5,
            ]
        ),
        resulting_paragraphs=mock_up_data,
        resulting_titles=mock_up_results,
    )
