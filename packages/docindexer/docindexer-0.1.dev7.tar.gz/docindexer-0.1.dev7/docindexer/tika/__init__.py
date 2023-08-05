# -*- coding: utf-8 -*-

import os
import json
import logging
import subprocess

logger = logging.getLogger(__name__)

JAR_PATH = os.path.join(os.path.dirname(__file__), "tika-app.jar")

def exec_stdout(args):
    """Run an application and capture standard output"""
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if err:
        logger.error(err)
    return out

def get_content(filepath):
    """Returns document plain-text content"""
    logger.debug("Getting plain-text content from %s with Tika", filepath)
    args = ('java', '-jar', JAR_PATH, '--text', filepath)
    text = exec_stdout(args)
    text = unicode(text, errors='ignore')
    return text

def get_metadata(filepath):
    """Returns a dict containing document metadata"""
    logger.debug("Getting json metadata from %s with Tika", filepath)
    args = ('java', '-jar', JAR_PATH, '--json', filepath)
    text = exec_stdout(args)
    meta = json.loads(out)
    return meta