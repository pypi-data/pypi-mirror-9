#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# library for Robot Framework to inspect python modules
#
import os.path
from base64 import b64encode, b64decode
from tempfile import NamedTemporaryFile as NTFile

import sh

import edeposit.amqp.calibre as calibre


BASE_PATH = os.path.dirname(__file__)


class Inspector(object):
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def is_type_of(self, element, reference):
        if type(element) != reference:
            raise AssertionError(
                "type(%s) != %s" % (str(type(element)), str(reference))
            )

    def call(self, fn, *args, **kwargs):
        return fn(*args, **kwargs)

    def length(self, val):
        return len(val)

    def has_attribute(self, obj, attr):
        return hasattr(obj, attr)

    def to_utf8(self, s):
        return s.decode("utf-8")

    def save_response(self, resp):
        with NTFile(mode="wb",
                    suffix="." + resp.format,
                    dir="/tmp",
                    delete=False) as ifile:
            ifile.write(b64decode(resp.b64_data))
            return ifile.name

    def check_ebook_convert_presence(self):
        """
        Check, if the ``ebook-convert`` program is installed.

        Raises:
            UserWarning: if not.
        """
        try:
            output = sh.ebook_convert(_ok_code=[1])
        except sh.CommandNotFound:
            raise UserWarning(
                "'ebook-convert' not found. Do you have callibre installed?"
            )

        # check whether the output is really from ebook-convert
        if "Usage" not in output or "Convert an ebook" not in output:
            raise UserWarning(
                "'ebook-convert' reacts strangely. Post this to developers:\n\n"
                + b64encode(str(output))
            )
