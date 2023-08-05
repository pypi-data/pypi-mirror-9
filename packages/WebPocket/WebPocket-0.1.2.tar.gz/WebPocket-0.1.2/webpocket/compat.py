# -*- coding: utf-8 -*-

import sys

if sys.version_info >= (3, 0):
  from urllib.parse import urlsplit
else:
  from urlparse import urlsplit
