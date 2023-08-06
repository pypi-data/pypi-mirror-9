#!/usr/bin/env python
import os
import shlex
from subprocess import call
from sph import SerfHandler


class DNSLeave(SerfHandler):

    def __init__(self):
        super(DNSLeave, self).__init__()

    def run(self, payload):

        print("member leaved dns plugin")
        print("payload: " + payload)
        exit(0)
