import logging
import os
import signal
import StringIO
import sys
import time


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


shutdown_timeout = int(os.environ.get('CONSUMERISM_SHUTDOWN_TIME', 5))


class GracefulExit(object):
    def __init__(self, signum, handler, timeout=shutdown_timeout):
        self.signum = signum
        self.handler = handler
        self.timeout = timeout
        self.original_handler = signal.getsignal(signum)

    def graceful_handler(self, handler):
        def handle_and_exit_after_timeout(signum, frame):
            handler(signum, frame)
            time.sleep(self.timeout)
            sys.exit(0)
        return handle_and_exit_after_timeout

    def __enter__(self):
        signal.signal(self.signum, self.graceful_handler(self.handler))

    def __exit__(self, type, value, traceback):
        if type == KeyboardInterrupt:
            self.graceful_handler(self.handler)(signal.SIGINT, None)
        signal.signal(self.signum, self.original_handler)
