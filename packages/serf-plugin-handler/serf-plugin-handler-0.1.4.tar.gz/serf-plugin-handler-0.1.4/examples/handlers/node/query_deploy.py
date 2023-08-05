#!/usr/bin/env python
import os
import shlex
from subprocess import call
from sph import SerfHandler


class NodeJoin(SerfHandler):

    def __init__(self):
        super(NodeJoin, self).__init__()

    def run(self, payload):

        print("member joined in dns plugin")
        print("payload: " + payload)
        exit(0)
