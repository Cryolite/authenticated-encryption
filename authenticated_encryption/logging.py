#!/usr/bin/env python3

import logging


def setup_logging(level: int) -> None:
    logging.basicConfig(
        format='%(asctime)s: %(filename)s:%(lineno)d: %(funcName)s:'
        ' %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S', level=level)
