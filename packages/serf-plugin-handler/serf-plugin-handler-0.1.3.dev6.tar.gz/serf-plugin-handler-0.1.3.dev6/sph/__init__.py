#!/usr/bin/env python
import re
import os
import sys
import importlib
import fileinput
import logging
from subprocess import call
from collections import defaultdict
from ConfigParser import ConfigParser


EVENT_TYPES = [
    "member_join",
    "member_leave",
    "member_reap",
    "member_update",
    "member_failed",
    "query",
    "user"
]


config = ConfigParser()
config.read([
    os.path.join(sys.prefix, "etc/sph/sph.cfg"),
    "/etc/sph/sph.cfg",
    "sph.cfg"
])

class SerfHandler(object):

    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)
        self.name = os.environ["SERF_SELF_NAME"]
        self.role = (os.environ.get("SERF_TAG_ROLE") or
                     os.environ.get("SERF_SELF_ROLE"))
        for key in os.environ.keys():
			key = key.lower()
			if key[0:8] == "SERF_TAG":
				self.tags[key[9:]] = os.environ.get(key.upper())

        self.event_type = os.environ["SERF_EVENT"].replace("-", "_")

        if self.event_type == "user":
            self.event = os.environ["SERF_USER_EVENT"]
        elif self.event_type == "query":
            self.event = os.environ["SERF_QUERY_NAME"]
        else:
            self.event = os.environ["SERF_EVENT"].replace("-", "_")

    def log(self, message):
        self.logger.info("\n%s", message)

    def warn(self, message):
        self.logger.warn("\n%s", message)

    def run(self, payload):
        raise NotImplemented


class SerfRouter(SerfHandler):

    def __init__(self, root, auto_register=True):
        super(SerfRouter, self).__init__()
        self.root = root or "."
        self.handlers = {}
        for event_type in EVENT_TYPES:
            self.handlers[event_type] = defaultdict(list)
        self.handler_regexp = re.compile(
            "({})(?:_([^.]+)(?:\.py|\.sh))?".format("|".join(EVENT_TYPES)))

        if auto_register:
            self.register_all()

    def register(self, event_type, event, handler):
        self.handlers[event_type][event].append(handler)

    def register_all(self):
        for path, dirnames, filenames in os.walk(self.root, topdown=False):
            if not filenames:
                continue
            sys.path.append(path)
            self._find_handler_modules(filenames, path)
            sys.path.remove(path)

    def _find_handler_modules(self, files, path):
        for file_name in files:
            module_name, ext = os.path.splitext(file_name)
            if ext not in (".py", ".sh"):
                continue
            match = re.match(self.handler_regexp, file_name)
            if not match:
                continue
            event_type = match.group(1)
            event = match.group(2) or event_type
            if ext == ".py":
                self._import_handler(event_type, event, module_name)
            else:
                self.register(event_type, event, os.path.join(path, file_name))

    def _import_handler(self, event_type, event, module_name):
        module = importlib.import_module(module_name)
        for name, handler in module.__dict__.items():
            if name.startswith("_") or name == "SerfHandler":
                continue
            if (isinstance(handler, type) and
                    issubclass(handler, SerfHandler)):
                self.register(event_type, event, handler)

    def get_handlers(self):
        return self.handlers[self.event_type][self.event]

    def get_payload(self):
        return "".join(line for line in fileinput.input())

    def run(self):
        handlers = self.get_handlers()
        if not handlers:
            return
        payload = self.get_payload()
        return any(self._invoke(handler, payload) for handler in handlers)


    def _invoke(self, handler, payload):
        return_code = 1
        if isinstance(handler, str):
            return_code = call([handler, payload], shell=True)
        elif issubclass(handler, SerfHandler):
            instance = handler()
            try:
                return_code = instance.run(payload)
            except Exception:
                self.logger.exception("Handler invocation failed!")
        return return_code
