# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
import argparse
import os
import re
import sys
import subprocess
import time
from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import urlencode

# - uruchamianie testów z pokryciem kodu
# - zapis wyniku testów do logu
# - jeżeli testy powiodły się - na zielono wyświetl ilość uruchomionych testów
# i poziom pokrycia kodu
# - jeżeli wystąpił błąd w testach - na pomarańczowo wyświetl ilość
# uruchomionych testów i poziom pokrycia kodu
# - jeżeli testy nie przeszły - na czerwono wyświetl ilość uruchomionych testów
# i poziom pokrycia kodu
# - jeżeli jakiś plik zmienił się, uruchom ponownie test
DEFAULT_COLORS = {
    'red': 41,
    'green': 42,
    'blue': 44,
    'sea': 46,
}


class IObservable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def register(self, observer):
        pass  # pragma nocover

    @abstractmethod
    def notify_observers(self, *args, **kwargs):
        pass  # pragma nocover


class IObserver(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def notify(self, observable, *args, **kwargs):
        pass  # pragma nocover


class StatusDisplay(IObserver, object):
    """ <<sink>>

    Responsibilities:

        - print status information
    """
    def notify(self, observable, *args, **kwargs):
        ran, failures, errors, coverage = args
        # first run
        if self._first_run:
            self._write_header()
            self._first_run = False
        if ran is None:
            self._write_empty()
        else:
            self._write(ran, failures, errors, coverage)

    @abstractmethod
    def _write(self, ran, failures, errors, coverage):
        pass  # pragma nocover

    @abstractmethod
    def _write_header(self):
        pass  # pragma nocover

    @abstractmethod
    def _write_empty(self):
        pass  # pragma nocover


class BWDisplay(StatusDisplay):
    """ <<sink>>

    Responsibilities:

        - print status information
    """
    pattern = '%(color)s %(num)8d%(failures)9d%(errors)8d%(coverage)8d%%\n'
    empty_pattern = '%(color)s%(space)28s%(space)8s%%\n'

    def __init__(self, output=None, colors=None):
        """@todo: Docstring for __init__

        :param output: file to which write
        :param colors: color codes used to display status
        """
        self._output = output if output is not None else sys.stdout
        self._first_run = True

    def _write_header(self):
        self._output.write('      Tests ran Failures  Errors Coverage\n')

    def _write_empty(self):
        self._output.write('\n')

    def _write(self, ran, failures, errors, coverage):
        """ Display status information.

        :param ran: number of tests run
        :param failures: number of failures
        :param errors: number of errors
        :param coverage: coverage percent
        """
        if failures or errors:
            color = 'FAIL: '
        else:
            color = 'OK:   '
        line = self.pattern % {
            'color': color,
            'num': ran,
            'failures': failures,
            'errors': errors,
            'coverage': coverage,
        }
        self._output.write(line)


class ColorDisplay(StatusDisplay):
    """ <<sink>>

    Responsibilities:

        - print status information
    """
    pattern = '%(color)s %(num)8d%(failures)9d%(errors)8d%(coverage_color)s%(coverage)8d%%%(normal_color)s\n'
    empty_pattern = '%(color)s%(space)28s%(coverage_color)s%(space)8s%%%(normal_color)s\n'

    def __init__(self, output=None, colors=None):
        """@todo: Docstring for __init__

        :param output: file to which write
        :param colors: color codes used to display status
        """
        self._output = output if output is not None else sys.stdout
        self._colors = colors if colors is not None else DEFAULT_COLORS
        self._last_run_color = ''
        self._last_run_cov_color = ''
        self._first_run = True

    def _write_header(self):
        self._output.write('Tests ran Failures  Errors Coverage\n')

    def _write_empty(self):
        self._output.write('\n')

    def _write(self, ran, failures, errors, coverage):
        """ Display status information.

        :param ran: number of tests run
        :param failures: number of failures
        :param errors: number of errors
        :param coverage: coverage percent
        """
        if failures or errors:
            color = self._colors['red']
            coverage_color = color
        else:
            green = self._colors['green']
            blue = self._colors['blue']
            if self._last_run_color in [green, blue]:
                color = blue
            else:
                color = green
            if coverage < 100:
                coverage_color = self._colors['sea']
            else:
                coverage_color = color
        self._last_run_color = color
        self._last_run_cov_color = coverage_color
        line = self.pattern % {
            'color': '\033[%sm' % color,
            'num': ran,
            'failures': failures,
            'errors': errors,
            'coverage_color': '\033[%sm' % coverage_color if coverage_color != color else '',
            'coverage': coverage,
            'normal_color': '\033[0m',
        }
        self._output.write(line)


class RemoteDisplay(IObserver, object):
    """ <<sink>>

    Responsibilities:

        - send status information to central server
    """

    def __init__(self, url, name):
        self._name = name
        self._url = url

    def notify(self, observable, *args, **kwargs):
        ran, failures, errors, coverage = args
        self._send(ran, failures, errors, coverage)

    def _send(self, ran, failures, errors, coverage):
        """ Send status information.

        :param ran: number of tests run
        :param failures: number of failures
        :param errors: number of errors
        :param coverage: coverage percent
        """
        data = {
            'name': self._name,
            'ran': ran,
            'failures': failures,
            'errors': errors,
            'coverage': coverage
        }
        data = urlencode(data)
        response = urlopen(self._url, data)
        return response


class AbstractWriter(object):

    def write(self, text):
        raise NotImplementedError  # pragma nocover


class DummyWriter(AbstractWriter):

    def write(self, text):
        pass


class LogWriter(AbstractWriter):
    """ <<sink>>

    Responsibilities:

        - write logs
    """

    def __init__(self, output):
        """@todo: Docstring for __init__

        :param output: @todo
        :returns: @todo

        """
        self._output = output
        self._last_traceback = []

    def write(self, text):
        """@todo: Docstring for write

        :param text: @todo
        :returns: @todo

        """
        to_diff = text.splitlines()
        to_diff = [line for line in to_diff if not line.startswith('Ran')]
        if to_diff != self._last_traceback:
            self._output.write(text)
            self._output.flush()
            self._last_traceback = to_diff


class TestRunner(object):
    """ <<source>>

    Responsibilities:

        - run tests
    """
    def __init__(self, command):
        """@todo: Docstring for __init__

        :param command: @todo
        :returns: @todo

        """
        self._command = command

    def run(self):
        """@todo: Docstring for run
        :returns: @todo
        """
        command = [
            'coverage', 'run',
            '--branch',
            '--source', '.',
        ] + self._command.split()
        program_output, test_output = self._run_command(command)
        command = ['coverage', 'report']
        report_output, error_output = self._run_command(command)
        return (str(program_output), str(test_output + report_output))

    def _run_command(self, command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdoutdata, stderrdata = process.communicate()
        return stdoutdata, stderrdata


class TestResultParser(object):
    """ <<filter>>

    Responsibilities:

        - parse test result
    """

    def parse(self, input_data):
        lines = input_data.splitlines()
        lines.reverse()
        ran = self._get_ran_tests_num(lines)
        failures, errors = self._get_failures(lines)
        coverage = self._get_coverage(lines)
        return (ran, failures, errors, coverage)

    def _get_failures(self, lines):
        error_re = re.compile('^(?:OK|FAILED)(?:\s*\((?:failures=(\d+))?(?:,\s*)?(?:errors=(\d+))?)')
        failures = 0
        errors = 0
        for line in lines:
            match = error_re.search(line)
            if match:
                failures = int(match.group(1) or 0)
                errors = int(match.group(2) or 0)
                return failures, errors
        return failures, errors

    def _get_ran_tests_num(self, lines):
        ran_re = re.compile('^Ran (\d+)')
        ran = 0
        for line in lines:
            match = ran_re.search(line)
            if match:
                return int(match.group(1) or 0)
        return ran

    def _get_coverage(self, lines):
        total_re = re.compile('^[^\s]+\s*\d+\s*\d+\s*\d+\s*\d+\s*(\d+)%')
        total = 0
        for line in lines:
            match = total_re.search(line)
            if match:
                return int(match.group(1) or 0)
        return total


class FileMonitorTimeoutError(Exception):
    pass


class FileMonitor(object):
    """ <<source>>

    Responsibilities:

        - monitor file changes
    """
    def __init__(self, timeout=60, interval=2, monitored_extensions=['.py']):
        self._mtimes = {}
        self._timeout = timeout
        self._interval = interval
        self._monitored_extensions = monitored_extensions

    def wait_for_change(self):
        """@todo: Docstring for wait_for_change
        :returns: @todo

        """
        time_passed = 0
        while not self.code_has_changed():
            time.sleep(self._interval)
            time_passed += self._interval
            if time_passed > self._timeout:
                raise FileMonitorTimeoutError
        return True

    def code_has_changed(self):
        files = self.get_monitored_files()
        for filename in files:
            if self.file_has_changed(filename):
                return True
        return False

    def get_monitored_files(self):
        for dirpath, dirnames, filenames in os.walk('.'):
            for filename in filenames:
                if self.should_monitor_file(filename):
                    yield os.path.join(dirpath, filename)

    def should_monitor_file(self, filename):
        file_extension = os.path.splitext(filename)[1]
        return file_extension in self._monitored_extensions

    def file_has_changed(self, filename):
        curr_mtime = os.stat(filename).st_mtime
        last_mtime = self._mtimes.setdefault(filename, curr_mtime)
        self._mtimes[filename] = curr_mtime
        return (curr_mtime != last_mtime)


class TddMon(IObservable, object):
    """ <<controller>>

    Collaborators:

        - TestRunner - <<source>>
        - TestResultParser - <<filter>>
        - LogWriter - <<sink>>
        - IObserver - <<sink>>
        - FileMonitor - <<source>>
    """
    def __init__(self, filename, log=None, output=None):
        self.test_runner = TestRunner(filename)
        self.log_writer = LogWriter(log) if log is not None else DummyWriter()
        self.test_result_parser = TestResultParser()
        self.file_monitor = FileMonitor()
        self.server = LogWriter(log) if log is not None else DummyWriter()
        self._observers = []

    def register(self, observer):
        self._observers.append(observer)

    def notify_observers(self, *args, **kwargs):
        for observer in self._observers:
            observer.notify(self, *args, **kwargs)

    def run(self):
        """@todo: Docstring for run
        :returns: @todo

        """
        stdoutdata, stderrdata = self.test_runner.run()
        self.log_writer.write(stdoutdata + stderrdata)
        result = self.test_result_parser.parse(stderrdata)
        self.notify_observers(*result)

    def loop(self):
        self.run()
        try:
            while True:
                try:
                    self.file_monitor.wait_for_change()
                except FileMonitorTimeoutError:
                    self.notify_observers(None, None, None, None)
                else:
                    self.run()
        except KeyboardInterrupt:
            pass


def main(*args):
    """ Run test monitor
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-l', '--log', dest='log', type=argparse.FileType('a'))
    parser.add_argument('-s', '--server', dest='server')
    parser.add_argument('-n', '--name', dest='name')
    default_color = (sys.platform != 'win32')
    parser.add_argument('--nocolor', dest='color', default=default_color, action='store_false')
    result = parser.parse_args(*args)
    controller = TddMon(result.filename, log=result.log)
    if result.color:
        controller.register(ColorDisplay())
    else:
        controller.register(BWDisplay())
    if result.server and result.name:
        controller.register(RemoteDisplay(result.server, result.name))
    controller.loop()


if __name__ == '__main__':  # pragma nobranch
    main()  # pragma nocover
