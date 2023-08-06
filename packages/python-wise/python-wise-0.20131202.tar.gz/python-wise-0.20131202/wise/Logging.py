# -*- mode: python; coding: utf-8 -*-

import logging

logging.basicConfig()
logger = logging.getLogger("wise")
logger.setLevel(logging.DEBUG)

WHITE_BOLD = "01;01"
YELLOW_BOLD = "01;33"
RED_BOLD = "01;31"
WHITE_NORMAL = "01;00"


def _colourize(msg, color=WHITE_NORMAL):
    head = ""
    body = ""

    if ":" in msg:
        fields = msg.split(":")
        head, body = fields[0], ":".join(fields[1:])

    return "\033[{}m{}:\033[00m{}".format(color, head, body)


def info(msg):
    msg = _colourize(msg, WHITE_BOLD)
    logger.info(msg)


def warning(msg):
    msg = _colourize(msg, YELLOW_BOLD)
    logger.warning(msg)


def error(msg):
    msg = _colourize(msg, RED_BOLD)
    logger.error(msg)
