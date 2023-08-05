#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import time
import os.path
from string import Template
from tempfile import NamedTemporaryFile

import pyqrcode

from translator import gen_pdf


# Variables ===================================================================
DES_DIR = "resources"
RES_PATH = os.path.join(
    os.path.dirname(__file__),
    DES_DIR,
)


# Functions & classes =========================================================
def _resource_context(fn):
    """
    Compose path to the ``resources`` directory for given `fn`.

    Args:
        fn (str): Filename of file in ``resources`` directory.

    Returns:
        str: Absolute path to the file in resources directory.
    """
    return os.path.join(
        os.path.dirname(__file__),
        DES_DIR,
        fn
    )


def get_contract(firma, pravni_forma, sidlo, ic, dic, zastoupen):
    """
    Compose contract and create PDF.

    Args:
        firma (str): firma
        pravni_forma (str): pravni_forma
        sidlo (str): sidlo
        ic (str): ic
        dic (str): dic
        zastoupen (str): zastoupen

    Returns:
        obj: StringIO file instance containing PDF file.
    """
    contract_fn = _resource_context(
        "Licencni_smlouva_o_dodavani_elektronickych_publikaci"
        "_a_jejich_uziti.rst"
    )

    # load contract
    with open(contract_fn) as f:
        contract = f.read()#.decode("utf-8").encode("utf-8")

    # make sure that `firma` has its heading mark
    firma = firma.strip()
    firma = firma + ":\n" + ((len(firma) + 1) * "-")

    # patch template
    contract = Template(contract).substitute(
        firma=firma,
        pravni_forma=pravni_forma.strip(),
        sidlo=sidlo.strip(),
        ic=ic.strip(),
        dic=dic.strip(),
        zastoupen=zastoupen.strip(),
        resources_path=RES_PATH
    )

    return gen_pdf(
        contract,
        open(_resource_context("style.json")).read(),
    )


def get_review(review_struct):
    """
    Generate review from `review_struct`.

    Args:
        review_struct (obj): :class:`.GenerateReview` instance.

    Returns:
        obj: StringIO file instance containing PDF file.
    """
    review_fn = _resource_context("review.rst")

    # read review template
    with open(review_fn) as f:
        review = f.read()

    # generate qr code
    with NamedTemporaryFile(suffix=".png") as qr_file:
        url = pyqrcode.create(review_struct.internal_url)
        url.png(qr_file.name, scale=7)

        # save the file
        qr_file.flush()
        qr_file.seek(0)

        # generate template
        review = Template(review).substitute(
            content=review_struct.get_rst(),
            datum=time.strftime("%d.%m.%Y", time.localtime()),
            cas=time.strftime("%H:%M", time.localtime()),
            resources_path=RES_PATH,
            qr_path=qr_file.name,
        )

        return gen_pdf(
            review,
            open(_resource_context("review_style.json")).read(),
        )
