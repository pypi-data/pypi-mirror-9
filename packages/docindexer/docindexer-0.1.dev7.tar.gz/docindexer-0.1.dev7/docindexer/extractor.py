# -*- coding: utf-8 -*-
# Extract information from binary files

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from . import tika
import tempfile
import os
import logging

logger = logging.getLogger(__name__)


def run_with_tempfile(func, binary_data, filename):
    _, ext = os.path.splitext(filename)
    f = tempfile.NamedTemporaryFile(mode='w+b', 
            delete=False, suffix=ext)
    path = f.name
    with f:
        f.write(binary_data)
    out = func(path)
    os.unlink(path)
    return out

def get_content(binary_data, filename=''):
    logger.info("Get content from binary doc (bytes=%s, filename='%s')",
        len(binary_data), filename)
    return run_with_tempfile(tika.get_content, binary_data, filename)

def get_metadata(binary_data, filename=''):
    logger.info("Get metadata from binary doc (bytes=%s, filename='%s')",
        len(binary_data), filename)
    return run_with_tempfile(tika.get_metadata, binary_data, filename)

