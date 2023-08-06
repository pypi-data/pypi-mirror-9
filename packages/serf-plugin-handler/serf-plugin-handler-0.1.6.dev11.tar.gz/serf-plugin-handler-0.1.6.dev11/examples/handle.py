#!/usr/bin/env python

import os
import sys
import logging
from sph import SerfRouter


logging.basicConfig()


if __name__ == '__main__':
    base = os.path.join(os.path.dirname(__file__), "handlers")
    sys.exit(SerfRouter(base).run())
