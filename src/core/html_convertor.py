import os

from htmldocx import HtmlToDocx


def converting_to_doc(input_html, output_docx):
    new_parser = HtmlToDocx()
    input_file = os.path.dirname(os.path.abspath(__file__)) + f'/{input_html}'
    new_parser.parse_html_file(input_file, output_docx)
