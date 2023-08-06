#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from StringIO import StringIO
from tempfile import NamedTemporaryFile

from rst2pdf.createpdf import RstToPdf


# Variables ===================================================================
FOOTER = "###Page###/###Total###"  #:


# Functions & classes =========================================================
def _init_pdf(style_path, header=None, footer=FOOTER):
    """
    Initialize :class:`RstToPdf` class.

    Args:
        style_path (str): Path to the style for the PDF.
        header (str, default None): Header which will be rendered to each page.
        footer (str, default FOOTER): Footer, which will be rendered to each
               page. See :attr:`FOOTER` for details.

    Returns:
        obj: Initialized object.
    """
    return RstToPdf(
        language="cs",
        font_path=[
            "/usr/share/fonts",
            "/usr/share/fonts/truetype/",
            '.',
            '/usr/local/lib/python2.7/dist-packages/rst2pdf/fonts'
        ],
        stylesheets=[
            style_path
        ],
        breaklevel=0,
        splittables=True,
        header=header,
        footer=footer
    )


def gen_pdf(rst_content, style_text, header=None, footer=FOOTER):
    """
    Create PDF file from `rst_content` using `style_text` as style.

    Optinally, add `header` or `footer`.

    Args:
        rst_content (str): Content of the PDF file in restructured text markup.
        style_text (str): Style for the :mod:`rst2pdf` module.
        header (str, default None): Header which will be rendered to each page.
        footer (str, default FOOTER): Footer, which will be rendered to each
               page. See :attr:`FOOTER` for details.

    Returns:
        obj: StringIO file instance containing PDF file.
    """
    out_file_obj = StringIO()

    with NamedTemporaryFile() as f:
        f.write(style_text)
        f.flush()

        pdf = _init_pdf(f.name, header, footer)

    # create PDF
    pdf.createPdf(text=rst_content, output=out_file_obj, compressed=True)

    # rewind file pointer to begin
    out_file_obj.seek(0)

    return out_file_obj
