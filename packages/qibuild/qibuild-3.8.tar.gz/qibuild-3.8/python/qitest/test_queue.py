## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import contextlib
import collections
import datetime
import signal
import traceback
import time
import StringIO
import sys
import threading
import Queue

from qisys import ui
import qisys.command
import qitest.result


class TestQueue():
    """ A class able to run tests in parallel """
    def __init__(self, tests):
        self.tests = tests
        self.test_logger = TestLogger(tests)
        self.task_queue = Queue.Queue()
        self.launcher = None
        self.results = collections.OrderedDict()
        self.ok = False
        self._interrupted = False
        self.elapsed_time = 0
        self._workers = list()

    def run(self, num_jobs=1):
        """ Run all the tests """
        signal.signal(signal.SIGINT, self.sigint_handler)
        start = datetime.datetime.now()
        self._run(num_jobs=num_jobs)
        signal.signal(signal.SIGINT, signal.default_int_handler)
        end = datetime.datetime.now()
        delta = end - start
        self.elapsed_time = float(delta.microseconds) / 10**6 + delta.seconds
        self.summary()
        return self.ok

    def _run(self, num_jobs=1):
        """ Helper function for ._run """
        if not self.launcher:
            ui.error("test launcher not set, cannot run tests")
            return
        for i, test in enumerate(self.tests):
            self.task_queue.put((test, i))

        if num_jobs == 1:
            self.test_logger.single_job = True

        for i in range(0, num_jobs):
            worker = TestWorker(self.task_queue, i)
            worker.launcher = self.launcher
            worker.launcher.worker_index = i
            worker.test_logger = self.test_logger
            worker.results = self.results
            self._workers.append(worker)
            worker.start()

        while not self.task_queue.empty() and \
              not self._interrupted:
            time.sleep(0.1)

        for worker_thread in self._workers:
            worker_thread.join()

    def summary(self):
        """ Display the tests results.

        Called at the end of self.run()
        Sets ``self.ok``

        """
        if not self.tests:
            self.ok = False
            return
        num_tests = len(self.results)
        failures = [x for x in self.results.values() if x.ok is False]
        num_failed = len(failures)
        message = "Ran %i tests in %is" % (num_tests, self.elapsed_time)
        ui.info(message)
        self.ok = (not failures) and not self._interrupted
        if self.ok:
            ui.info(ui.green, "All pass. Congrats!")
            return
        if num_failed != 0:
            ui.error(num_failed, "failures")
        if failures:
            max_len = max(len(x.test["name"]) for x in failures)
            for i, failure in enumerate(failures):
                ui.info_count(i, num_failed,
                            ui.blue, failure.test["name"].ljust(max_len + 2),
                            ui.reset, *failure.message)

    def sigint_handler(self, *args):
        """ Called when user press ctr+c during the test suite

        * Tell qisys.command to kill every process still running
        * Tell the tests_queue that is has been interrupted, and
          stop all the test workers
        * Setup a second sigint for when killing process failed

        """
        def double_sigint(signum, frame):
            sys.exit("Exiting main program \n",
                       "This may leave orphan processes")
        qisys.command.SIGINT_EVENT.set()
        ui.warning("\n!!!",
                   "Interrupted by user, stopping every process.\n"
                   "This may take a few seconds")
        self._interrupted = True
        for worker in self._workers:
            worker.stop()
        signal.signal(signal.SIGINT, double_sigint)


class TestWorker(threading.Thread):
    """ Implementation of a 'worker' thread. It will consume
    the test queue, running the tests and logging the results

    """
    def __init__(self, queue, worker_index):
        super(TestWorker, self).__init__(name="TestWorker#%i" % worker_index)
        self.index = worker_index
        self.queue = queue
        self.launcher = None
        self.test_logger = None
        self.results = dict()
        self._should_stop = False

    def stop(self):
        """ Tell the worker it should stop trying to read items from the queue """
        self._should_stop = True

    def run(self):
        while not self._should_stop:
            try:
                test, index = self.queue.get_nowait()
            except Queue.Empty:
                return
            self.test_logger.on_start(test, index)
            result = None
            try:
                result = self.launcher.launch(test)
            except Exception, e:
                result = qitest.result.TestResult(test)
                result.ok = False
                result.message = self.message_for_exception(e)
            if not self._should_stop:
                self.test_logger.on_completed(test, index, result.message)
            self.results[test["name"]] = result
            self.queue.task_done()

    def message_for_exception(self, exception):
        tb = sys.exc_info()[2]
        io = StringIO.StringIO()
        traceback.print_tb(tb, file=io)
        return (ui.red, "Python exception during tests:\n",
                str(exception), "\n",
                ui.reset,
                io.getvalue())

class TestLogger:
    """ Small class used to print what is going on during
    tests, using a mutex so that outputs are not mixed up

    """
    def __init__(self, tests):
        self.mutex = threading.Lock()
        self.tests = tests
        try:
            self.max_len = max((len(x["name"]) for x in self.tests))
        except ValueError:
            self.max_len = 0
        self.single_job = False

    def on_start(self, test, index):
        """ Called when a test starts """
        if self.single_job:
            self._info(test, index, (), end="")
            return
        with self.mutex:
            self._info(test, index, ("starting ...",))

    def on_completed(self, test, index, message):
        """ Called when a test is over """
        if self.single_job:
            ui.info(*message)
            return
        with self.mutex:
            self._info(test, index, message)

    def _info(self, test, index, message, **kwargs):
        """ Helper method """
        ui.info_count(index, len(self.tests),
                      ui.blue, test["name"].ljust(self.max_len + 2),
                      ui.reset, *message, **kwargs)
