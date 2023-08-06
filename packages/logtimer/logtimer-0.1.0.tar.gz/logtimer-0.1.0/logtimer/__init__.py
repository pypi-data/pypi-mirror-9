

import time
import logging


logger = logging.getLogger(__name__)

class Timer:
    def __init__(self, name, logger=logger):
        self.name = name
        self.logger = logger
        self.exc_type = None
        self.exc_value = None
        self.traceback = None

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.end()
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.traceback = traceback
        self.log_completion()

    def start(self):
        self.start_processor_time = time.clock()
        self.start_wall_time = time.time()
        self.logger.debug('Starting %s at %f' % (self.name, self.start_wall_time))

    def end(self):
        self.end_processor_time = time.clock()
        self.end_wall_time = time.time()

    def log_completion(self):
        if self.exc_type is None:
            self.log_success()
        else:
            self.log_failure()

    def log_success(self):
        self.logger.info('Successfully completed %s (%s)' % (self.name, self.describe_time()))

    def log_failure(self):
        self.logger.warn(self.failure_message())

    def failure_message(self):
        msg = 'Failed running %s (%s) with exception %s (%s)' % (
            self.name,
            self.describe_time(),
            str(self.exc_type),
            str(self.exc_value)
            )
        return msg

    def describe_time(self):
        return "Wall Time: %f, Processor Time: %f" % (self.wall_duration(),
                self.processor_duration())

    def processor_duration(self):
        return self.end_processor_time - self.start_processor_time

    def wall_duration(self):
        return self.end_wall_time - self.start_wall_time
