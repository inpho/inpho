"""
multiprocessing-compatible LogHandler. This module will be rendered obsolete
once we upgrade to Python 2.7.1 and Python 3.2, when we can use
logging.handlers.QueueHandler and logging.handlers.QueueListener.

The solution is from StackOverflow:
http://stackoverflow.com/questions/641420/how-should-i-log-while-using-multiprocessing-in-python/1009560#1009560
"""

import logging
import multiprocessing
import Queue # for multiprocessing.Queue exceptions
import threading
import time

class MultiprocessingHandler(logging.Handler):
    def __init__(self, handler, queue, child=False):
        logging.Handler.__init__(self)

        self._handler = handler
        self.queue = queue

        # we only want one of the loggers to be pulling from the queue.
        # If there is a way to do this without needing to be passed this
        # information, that would be great!
        if child == False:
            self.shutdown = False
            self.polltime = 1
            t = threading.Thread(target=self.receive)
            t.daemon = True
            t.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def receive(self):
        while (self.shutdown == False) or (self.queue.empty() == False):
            try:
                # block for a short period of time to check for shutdown cases
                record = self.queue.get(True, self.polltime)
                self._handler.emit(record)
            except Queue.Empty, e:
                pass

    def send(self, s):
        # send just puts it in the queue for the server to retrieve
        self.queue.put(s)

    def _format_record(self, record):
        ei = record.exc_info
        if ei:
            dummy = self.format(record) # just to get traceback text into record.exc_text
            record.exc_info = None  # to avoid Unpickleable error

        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            # pass along these errors
            raise
        except:
            self.handleError(record)

    def close(self):
        time.sleep(self.polltime+1) # allow message to enter queue.
        self.shutdown = True
        time.sleep(self.polltime+1) # allow server to time out and see shutdown

    def __del__(self):
        self.close() # orderly shutdown when things are going poorly.

def f(x):
    # just a logging command...
    logging.critical('function number: ' + str(x))
    # make some calls take longer than others, to "jumble" output as in
    # real-world MP progs
    time.sleep(x % 3)

def initPool(queue, level):
    """
    This causes the logging module to be initialized with the necessary info
    in pool threads to work correctly.
    """
    logger = logging.getLogger('')
    logger.addHandler(
        MultiprocessingHandler(logging.StreamHandler(), queue, child=True))
    logger.setLevel(level)

def get_logging_pool():
    """
    Returns a multiprocessing.Pool object with MultiprocessingHandler loggers
    pre-configured.
    """
    return multiprocessing.Pool(initializer=initPool, 
        initargs=[logQueue, logging.getLogger('').getEffectiveLevel()])

if __name__ == '__main__':
    logQueue = multiprocessing.Queue(100)
    handler = MultiprocessingHandler(logging.FileHandler('file.log'), logQueue)
    logging.getLogger('').addHandler(handler)
    logging.getLogger('').setLevel(logging.DEBUG)

    logging.debug('starting main')

    # when bulding the pool on a Windows machine we also have to init the 
    # logger in all the instances with the queue and the level of logging.
    pool = get_logging_pool() 
    pool.map(f, range(0,50))
    pool.close()

    logging.debug('done')
    logging.shutdown()
