# -*- coding: utf-8 -*-

from __future__ import absolute_import

import contextlib
import threading
import uuid

ctx = threading.local()


class TrackerBase(object):
    def __init__(self, client=None, server=None):
        self.client = client
        self.server = server

    def handle(self, header):
        ctx.header = header
        ctx.counter = 0

    def gen_header(self, header):
        header.request_id = self.get_request_id()

        if not hasattr(ctx, "counter"):
            ctx.counter = 0

        ctx.counter += 1

        if not hasattr(ctx, "header"):
            header.seq = str(ctx.counter)
        else:
            header.seq = "{prev_seq}.{cur_counter}".format(
                prev_seq=ctx.header.seq, cur_counter=ctx.counter)

    def record(self, header, exception):
        pass

    @classmethod
    @contextlib.contextmanager
    def counter(cls, init=0):
        """Context for manually setting counter of seq number.

        :init: init value
        """
        if not hasattr(ctx, "counter"):
            ctx.counter = 0

        old = ctx.counter
        ctx.counter = init

        try:
            yield
        finally:
            ctx.counter = old

    @classmethod
    @contextlib.contextmanager
    def annotate(cls, **kwargs):
        ctx.annotation = kwargs
        try:
            yield ctx.annotation
        finally:
            del ctx.annotation

    @property
    def annotation(self):
        return ctx.annotation if hasattr(ctx, "annotation") else {}

    def get_request_id(self):
        if hasattr(ctx, "header"):
            return ctx.header.request_id
        return str(uuid.uuid4())


class ConsoleTracker(TrackerBase):
    def record(self, header, exception):
        print(header)
