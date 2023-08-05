# -*- coding: utf-8 -*-
from .fields import *  # noqa
with open("VERSION") as f:
    VERSION = __version__ = f.read()
