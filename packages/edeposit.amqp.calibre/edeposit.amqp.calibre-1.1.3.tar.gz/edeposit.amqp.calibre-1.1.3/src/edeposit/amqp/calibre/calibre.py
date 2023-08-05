#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
"""
Lowlevel conversion API for calibre's ``ebook-convert``.
"""
import os
from base64 import b64encode, b64decode
from tempfile import NamedTemporaryFile as NTFile


import sh


from structures import INPUT_FORMATS, OUTPUT_FORMATS, ConversionResponse


# Functions & objects =========================================================
def _wrap(text, columns=80):
    """
    Own "dumb" reimplementation of textwrap.wrap().

    This is because calling .wrap() on bigger strings can take a LOT of
    processor power. And I mean like 8 seconds of 3GHz CPU just to wrap 20kB of
    text without spaces.

    Args:
        text (str): Text to wrap.
        columns (int): Wrap after `columns` characters.

    Returns:
        str: Wrapped text.
    """
    out = []
    for cnt, char in enumerate(text):
        out.append(char)

        if (cnt + 1) % columns == 0:
            out.append("\n")

    return "".join(out)


def convert(input_format, output_format, b64_data):
    """
    Convert `b64_data` fron `input_format` to `output_format`.

    Args:
        input_format (str):  specification of input format (pdf/epub/whatever),
                             see :attr:`INPUT_FORMATS` for list
        output_format (str): specification of output format (pdf/epub/whatever),
                             see :attr:`OUTPUT_FORMATS` for list
        b64_data (str):      base64 encoded data

    Returns:
        ConversionResponse: namedtuple structure with information about output\
                            ``format``, data (``b64_data``) and ``protocol``\
                            from conversion. Structure is defined in \
                            :class:`.ConversionResponse`.

    Raises:
        AssertionError: when bad arguments are handed over
        UserWarning: when conversion failed
    """
    # checks
    assert input_format in INPUT_FORMATS, "Unsupported input format!"
    assert output_format in OUTPUT_FORMATS, "Unsupported output format!"

    with NTFile(mode="wb", suffix="." + input_format, dir="/tmp") as ifile:
        ofilename = ifile.name + "." + output_format

        # save received data to the temporary file
        ifile.write(
            b64decode(b64_data)
        )
        ifile.flush()

        # convert file
        try:
            output = ""
            with NTFile(mode="wb", suffix = ".stdout", dir="/tmp") as stdout:
                sh.ebook_convert(ifile.name, ofilename, _out=stdout).wait()
                stdout.flush()
                output = open(stdout.name).read()
                stdout.close()
        except sh.ErrorReturnCode_1, e:
            raise UserWarning(
                "Conversion failed:\n" +
                e.message.encode("utf-8", errors='ignore')
            )

        if output_format.upper() + " output written to" not in output:
            raise UserWarning("Conversion failed:\n" + output)

        # read the data from the converted file
        output_data = None
        with open(ofilename, "rb") as ofile:
            output_data = ofile.read()

        # remove temporary
        os.remove(ofilename),

        return ConversionResponse(
            format=output_format,
            b64_data=_wrap(b64encode(output_data)),
            protocol=output
        )
