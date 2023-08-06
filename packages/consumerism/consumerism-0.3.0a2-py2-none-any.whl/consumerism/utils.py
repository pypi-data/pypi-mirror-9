import logging
import StringIO


class LogCapture(object):
    def __init__(self, logger):
        self.logger = logger
        self.buffer = StringIO.StringIO()
        self.handler = logging.StreamHandler(self.buffer)
        self._output = None

    def output(self):
        return self._output

    def __enter__(self):
        self.logger.addHandler(self.handler)
        return self

    def __exit__(self, type, value, traceback):
        self.logger.removeHandler(self.handler)

        self._output = self.buffer.getvalue()
        self.buffer.close()
