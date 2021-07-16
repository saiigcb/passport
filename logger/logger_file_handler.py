"""Handle logger File generation"""
import logging
import os
from datetime import datetime
import time

class SizedTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    Handler for logging to a set of files, which switches from one file
    to the next when the current file reaches a certain size, or at certain
    timed intervals
    """

    def __init__(self, path, filename, mode, maxMegaBytes=0, backupCount=0, encoding=None,
                 delay=0, when='d', interval=1, utc=False):
        filename = datetime.now().strftime(filename + '_%Y_%m_%d.log')
        if path is None or not path.strip():
            path = "./logs"
        path = path + "/"
        if not os.path.exists(path):
            os.mkdir(path)
        filename = path + "/" + filename
        logging.handlers.TimedRotatingFileHandler.__init__(
            self, filename=filename, when=when, interval=interval,
            backupCount=backupCount, encoding=encoding, delay=delay, utc=utc)
        self.maxBytes = maxMegaBytes * 1024 * 1024

    def shouldRollover(self, record):
        """
        Determine if rollover should occur.

        Basically, see if the supplied record would cause the file to exceed
        the size limit we have.
        """
        if self.stream is None:                 # delay was set...
            self.stream = self._open()
        if self.maxBytes > 0:                   # are we rolling over?
            msg = "%s\n" % self.format(record)
            # due to non-posix-compliant Windows feature
            self.stream.seek(0, 2)
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return 1
        timer = int(time.time())
        if timer >= self.rolloverAt:
            return 1
        return 0
