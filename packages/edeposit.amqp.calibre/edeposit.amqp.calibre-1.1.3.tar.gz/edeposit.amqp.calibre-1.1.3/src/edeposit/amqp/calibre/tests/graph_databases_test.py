#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import calibre

import base64

gd = base64.b64encode(open("GraphDatabases.epub").read())
req = calibre.structures.ConversionRequest("epub", "pdf", gd)
resp = calibre.reactToAMQPMessage(req, "asd")

print resp.protocol

with open("GraphDatabases.pdf", "wb") as f:
    f.write(base64.b64decode(resp.b64_data))
