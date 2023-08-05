#!/usr/bin/env python
# -*- coding: utf-8 -*-

import types
import unittest

from mock import patch, call, sentinel, Mock
from six.moves import StringIO
from six.moves.urllib.parse import urlencode
from smarttest.decorators import test_type

from tddmon import (main, ColorDisplay, DEFAULT_COLORS, LogWriter,
                    TestRunner, TestResultParser, FileMonitor,
                    FileMonitorTimeoutError, TddMon, RemoteDisplay,
                    BWDisplay)


@test_type('unit')
class MainTestCase(unittest.TestCase):
    """ Test :py:meth:`main`. """

    @patch('tddmon.__main__.sys.stderr')
    def test_should_raise_exception_if_no_filename(self, stderr):
        """ Scenariusz: brak podanego pliku """
        # Arrange
        # Act
        # Assert
        self.assertRaises(SystemExit, main, [])

    @patch('tddmon.__main__.TddMon')
    @patch('tddmon.__main__.ColorDisplay')
    def test_should_return_filename_when_filename_given(self, ColorDisplay, TddMon):
        """ Scenariusz: podany tylko plik """
        # Arrange
        # Act
        filename = 'plik.py'
        main([filename])
        # Assert
        TddMon.assert_called_once_with(filename, log=None)
        tddmon = TddMon()
        tddmon.loop.assert_called_once_with()
        tddmon.register.assert_has_calls([call(ColorDisplay())])

    @patch('tddmon.__main__.TddMon')
    @patch('tddmon.__main__.ColorDisplay')
    @patch('tddmon.__main__.RemoteDisplay')
    def test_should_register_remote_display_on_url_and_name(self, RemoteDisplay, ColorDisplay, TddMon):
        """ Scenariusz: wysylanie do zdalnego serwera """
        # Arrange
        # Act
        filename = 'plik.py'
        main(['-s', 'example.com', '-n', 'username', filename])
        # Assert
        TddMon.assert_called_once_with(filename, log=None)
        tddmon = TddMon()
        tddmon.loop.assert_called_once_with()
        tddmon.register.assert_has_calls([call(ColorDisplay()), call(RemoteDisplay())])

    @patch('tddmon.__main__.TddMon')
    @patch('tddmon.__main__.ColorDisplay')
    @patch('tddmon.__main__.RemoteDisplay')
    def test_should_not_register_remote_display_if_no_url(self, RemoteDisplay, ColorDisplay, TddMon):
        """ Scenariusz: brak parametru url """
        # Arrange
        # Act
        filename = 'plik.py'
        main(['-n', 'username', filename])
        # Assert
        TddMon.assert_called_once_with(filename, log=None)
        tddmon = TddMon()
        tddmon.loop.assert_called_once_with()
        tddmon.register.assert_has_calls([call(ColorDisplay())])

    @patch('tddmon.__main__.TddMon')
    @patch('tddmon.__main__.ColorDisplay')
    @patch('tddmon.__main__.RemoteDisplay')
    def test_should_not_register_remote_display_if_no_name(self, RemoteDisplay, ColorDisplay, TddMon):
        """ Scenariusz: brak parametru name """
        # Arrange
        # Act
        filename = 'plik.py'
        main(['-n', 'username', filename])
        # Assert
        TddMon.assert_called_once_with(filename, log=None)
        tddmon = TddMon()
        tddmon.loop.assert_called_once_with()
        tddmon.register.assert_has_calls([call(ColorDisplay())])

    @patch('tddmon.__main__.TddMon')
    @patch('tddmon.__main__.BWDisplay')
    def test_should_register_bwdisplay_if_no_color_param(self, BWDisplay, TddMon):
        """ Scenariusz: brak koloru """
        # Arrange
        # Act
        filename = 'plik.py'
        main(['--nocolor', filename])
        # Assert
        TddMon.assert_called_once_with(filename, log=None)
        tddmon = TddMon()
        tddmon.loop.assert_called_once_with()
        tddmon.register.assert_has_calls([call(BWDisplay())])


@test_type('unit')
class ColorDisplayNotifyTestCase(unittest.TestCase):
    """ Test :py:meth:`ColorDisplay.notify`. """

    def setUp(self):
        self.output = StringIO()
        self.obj = ColorDisplay(self.output)
        super(ColorDisplayNotifyTestCase, self).setUp()

    def test_should_print_header_on_first_line(self):
        """ Scenariusz: pierwszy wynik """
        # Arrange
        # Act
        self.obj.notify(sentinel.observable, None, None, None, None)
        # Assert
        expected = 'Tests ran Failures  Errors Coverage\n'
        result = self.output.getvalue()
        self.assertTrue(result.startswith(expected))

    def test_should_print_empty_line(self):
        """ Scenariusz: brak danych - timeout """
        # Arrange
        # Act
        self.obj.notify(sentinel.observable, None, None, None, None)
        # Assert
        expected = '\n'
        result = self.output.getvalue()
        self.assertTrue(result.endswith(expected))

    def test_should_write_in_green_on_successful_run(self):
        """ Scenariusz: testy zakończone sukcesem """
        # Arrange
        # Act
        num, failures, errors, coverage = 1, 0, 0, 100
        self.obj.notify(sentinel.observable, num, failures, errors, coverage)
        # Assert
        color = DEFAULT_COLORS['green']
        expected = self._prepare_expected(color, failures, errors, num, coverage)
        result = self.output.getvalue()
        self.assertTrue(result.endswith(expected))

    def test_should_write_in_red_on_failed_run(self):
        """ Scenariusz: testy zakończone porażką """
        # Arrange
        # Act
        num, failures, errors, coverage = 1, 1, 0, 80
        self.obj.notify(sentinel.observable, num, failures, errors, coverage)
        # Assert
        color = DEFAULT_COLORS['red']
        expected = self._prepare_expected(color, failures, errors, num, coverage)
        result = self.output.getvalue()
        self.assertTrue(result.endswith(expected))

    def test_should_write_in_green_if_no_tests(self):
        """ Scenariusz: brak testów """
        # Arrange
        # Act
        num, failures, errors, coverage = 0, 0, 0, 0
        self.obj.notify(sentinel.observable, num, failures, errors, coverage)
        # Assert
        color = DEFAULT_COLORS['green']
        sea = DEFAULT_COLORS['sea']
        expected = self._prepare_expected(color, failures, errors, num,
                                          coverage, coverage_color=sea)
        result = self.output.getvalue()
        self.assertTrue(result.endswith(expected))

    def test_should_write_in_red_if_error_occure(self):
        """ Scenariusz: wystąpiły błędy """
        # Arrange
        # Act
        num, failures, errors, coverage = 1, 0, 1, 50
        self.obj.notify(sentinel.observable, num, failures, errors, coverage)
        # Assert
        color = DEFAULT_COLORS['red']
        expected = self._prepare_expected(color, failures, errors, num, coverage)
        result = self.output.getvalue()
        self.assertTrue(result.endswith(expected))

    def test_should_write_in_green_and_sea_on_successful_run_with_not_fully_covered(self):
        """ Scenariusz: testy zakończone sukcesem ale nie pełne pokrycie"""
        # Arrange
        # Act
        num, failures, errors, coverage = 1, 0, 0, 50
        self.obj.notify(sentinel.observable, num, failures, errors, coverage)
        # Assert
        color = DEFAULT_COLORS['green']
        sea = DEFAULT_COLORS['sea']
        expected = self._prepare_expected(color, failures, errors, num,
                                          coverage, coverage_color=sea)
        result = self.output.getvalue()
        self.assertTrue(result.endswith(expected))

    def test_should_write_in_blue_on_repeated_green(self):
        """ Scenariusz: ponowne uruchomienie na zielono """
        # Arrange
        # Act
        num, failures, errors, coverage = 1, 0, 0, 100
        self.obj.notify(sentinel.observable, num, failures, errors, coverage)
        self.obj.notify(sentinel.observable, num, failures, errors, coverage)
        # Assert
        color = DEFAULT_COLORS['green']
        expected = self._prepare_expected(color, failures, errors, num, coverage)
        color = DEFAULT_COLORS['blue']
        expected += self._prepare_expected(color, failures, errors, num, coverage)
        result = self.output.getvalue()
        self.assertTrue(result.endswith(expected))

    def _prepare_expected(self, color, failures, errors, num, coverage, coverage_color=None):
        coverage_color = coverage_color if coverage_color is not None else color
        expected = ColorDisplay.pattern % {
            'color': '\033[%sm' % color,
            'num': num,
            'failures': failures,
            'errors': errors,
            'coverage_color': '\033[%sm' % coverage_color if coverage_color != color else '',
            'coverage': coverage,
            'normal_color': '\033[0m',
        }
        return expected


@test_type('unit')
class BWDisplayNotifyTestCase(unittest.TestCase):
    """ Test :py:meth:`BWDisplay.notify`. """

    def setUp(self):
        self.output = StringIO()
        self.obj = BWDisplay(self.output)
        super(BWDisplayNotifyTestCase, self).setUp()

    def test_should_print_header_on_first_line(self):
        """ Scenariusz: pierwszy wynik """
        # Arrange
        # Act
        self.obj.notify(sentinel.observable, None, None, None, None)
        # Assert
        expected = '      Tests ran Failures  Errors Coverage\n'
        result = self.output.getvalue()
        self.assertTrue(result.startswith(expected))

    def test_should_print_empty_line(self):
        """ Scenariusz: brak danych - timeout """
        # Arrange
        # Act
        self.obj.notify(sentinel.observable, None, None, None, None)
        # Assert
        expected = '\n'
        result = self.output.getvalue()
        self.assertTrue(result.endswith(expected))

    def test_should_write_in_green_on_successful_run(self):
        """ Scenariusz: testy zakończone sukcesem """
        # Arrange
        # Act
        num, failures, errors, coverage = 1, 0, 0, 100
        self.obj.notify(sentinel.observable, num, failures, errors, coverage)
        # Assert
        color = 'OK:   '
        expected = self._prepare_expected(color, failures, errors, num, coverage)
        result = self.output.getvalue()
        self.assertTrue(result.endswith(expected))

    def test_should_write_in_red_on_failed_run(self):
        """ Scenariusz: testy zakończone porażką """
        # Arrange
        # Act
        num, failures, errors, coverage = 1, 1, 0, 80
        self.obj.notify(sentinel.observable, num, failures, errors, coverage)
        # Assert
        color = 'FAIL: '
        expected = self._prepare_expected(color, failures, errors, num, coverage)
        result = self.output.getvalue()
        self.assertTrue(result.endswith(expected))

    def test_should_write_in_green_if_no_tests(self):
        """ Scenariusz: brak testów """
        # Arrange
        # Act
        num, failures, errors, coverage = 0, 0, 0, 0
        self.obj.notify(sentinel.observable, num, failures, errors, coverage)
        # Assert
        color = 'OK:   '
        expected = self._prepare_expected(color, failures, errors, num, coverage)
        result = self.output.getvalue()
        self.assertTrue(result.endswith(expected))

    def test_should_write_in_red_if_error_occure(self):
        """ Scenariusz: wystąpiły błędy """
        # Arrange
        # Act
        num, failures, errors, coverage = 1, 0, 1, 50
        self.obj.notify(sentinel.observable, num, failures, errors, coverage)
        # Assert
        color = 'FAIL: '
        expected = self._prepare_expected(color, failures, errors, num, coverage)
        result = self.output.getvalue()
        self.assertTrue(result.endswith(expected))

    def test_should_write_in_green_and_sea_on_successful_run_with_not_fully_covered(self):
        """ Scenariusz: testy zakończone sukcesem ale nie pełne pokrycie"""
        # Arrange
        # Act
        num, failures, errors, coverage = 1, 0, 0, 50
        self.obj.notify(sentinel.observable, num, failures, errors, coverage)
        # Assert
        color = 'OK:   '
        expected = self._prepare_expected(color, failures, errors, num, coverage)
        result = self.output.getvalue()
        self.assertTrue(result.endswith(expected))

    def test_should_write_in_blue_on_repeated_green(self):
        """ Scenariusz: ponowne uruchomienie na zielono """
        # Arrange
        # Act
        num, failures, errors, coverage = 1, 0, 0, 100
        self.obj.notify(sentinel.observable, num, failures, errors, coverage)
        self.obj.notify(sentinel.observable, num, failures, errors, coverage)
        # Assert
        color = 'OK:   '
        expected = self._prepare_expected(color, failures, errors, num, coverage)
        color = 'OK:   '
        expected += self._prepare_expected(color, failures, errors, num, coverage)
        result = self.output.getvalue()
        self.assertTrue(result.endswith(expected))

    def _prepare_expected(self, color, failures, errors, num, coverage, coverage_color=None):
        expected = BWDisplay.pattern % {
            'color': color,
            'num': num,
            'failures': failures,
            'errors': errors,
            'coverage': coverage,
        }
        return expected


@test_type('unit')
class LogWriterWriteTestCase(unittest.TestCase):
    """ Test :py:meth:`LogWriter.write`. """

    def test_should_write_traceback_to_file_on_first_run(self):
        """ Scenariusz: pierwszy zapis """
        # Arrange
        output = StringIO()
        obj = LogWriter(output)
        # Act
        traceback = 'some traceback'
        obj.write(traceback)
        # Assert
        self.assertEqual(output.getvalue(), traceback)

    def test_should_not_write_to_file_if_nothing_has_changed(self):
        """ Scenariusz: brak zmiany """
        # Arrange
        output = StringIO()
        obj = LogWriter(output)
        # Act
        traceback = 'some traceback'
        obj.write(traceback)
        obj.write(traceback)
        # Assert
        self.assertEqual(output.getvalue(), traceback)

    def test_should_ignore_run_time_change(self):
        """ Scenariusz: ignorowanie czasu wykonania """
        # Arrange
        output = StringIO()
        obj = LogWriter(output)
        # Act
        first_traceback = '''
.F..
======================================================================
FAIL: test_should_return_buzz_on_5 (__main__.FizzbuzzTestCase)
Scenariusz: liczba buzz
----------------------------------------------------------------------
Traceback (most recent call last):
File "fizzbuzz.py", line 51, in test_should_return_buzz_on_5
    assert False
AssertionError

----------------------------------------------------------------------
Ran 4 tests in 0.001s

FAILED (failures=1)'''
        second_traceback = '''
.F..
======================================================================
FAIL: test_should_return_buzz_on_5 (__main__.FizzbuzzTestCase)
Scenariusz: liczba buzz
----------------------------------------------------------------------
Traceback (most recent call last):
File "fizzbuzz.py", line 51, in test_should_return_buzz_on_5
    assert False
AssertionError

----------------------------------------------------------------------
Ran 4 tests in 0.003s

FAILED (failures=1)'''
        obj.write(first_traceback)
        obj.write(second_traceback)
        # Assert
        self.assertEqual(output.getvalue(), first_traceback)


@test_type('unit')
class TestRunnerRunTestCase(unittest.TestCase):
    """ Test :py:meth:`TestRunner.run`. """

    @patch('subprocess.Popen')
    def test_should_return_program_output_with_coverage_report(self, Popen):
        """ Scenariusz: uruchomienie testu z pokryciem kodu """
        # Arrange
        process = Popen.return_value
        process.communicate.side_effect = [('', 'OK'), ('TOTAL', '')]
        command = 'test_command.py'
        obj = TestRunner(command)
        # Act
        stdoutdata, stderrdata = obj.run()
        # Assert
        self.assertEqual(stderrdata, 'OKTOTAL')
        self.assertEqual(len(Popen.call_args_list), 2)
        self.assertTrue(command in Popen.call_args_list[0][0][0])


@test_type('unit')
class TestResultParserParseTestCase(unittest.TestCase):
    """ Test :py:meth:`TestResultParser.parse`. """

    def test_should_return_0_test_num_on_empty_run(self):
        """ Scenariusz: 1 poprawny test """
        # Arrange
        obj = TestResultParser()
        input_data = ''
        # Act
        result = obj.parse(input_data)
        # Assert
        self.assertEqual(result, (0, 0, 0, 0))

    def test_should_return_1_test_num_on_success(self):
        """ Scenariusz: 1 poprawny test """
        # Arrange
        obj = TestResultParser()
        input_data = '''
Ran 1 tests in 0.001s
OK
'''
        # Act
        result = obj.parse(input_data)
        # Assert
        self.assertEqual(result, (1, 0, 0, 0))

    def test_should_return_2_test_num_on_success(self):
        """ Scenariusz: 2 poprawne testy """
        # Arrange
        obj = TestResultParser()
        input_data = '''
Ran 2 tests in 0.001s
OK
'''
        # Act
        result = obj.parse(input_data)
        # Assert
        self.assertEqual(result, (2, 0, 0, 0))

    def test_should_return_failures_num_on_failure(self):
        """ Scenariusz: testy niepoprawne """
        # Arrange
        obj = TestResultParser()
        input_data = '''
Ran 1 tests in 0.001s
FAILED (failures=1)
'''
        # Act
        result = obj.parse(input_data)
        # Assert
        self.assertEqual(result, (1, 1, 0, 0))

    def test_should_return_coverage_on_success(self):
        """ Scenariusz: wyniki z pokryciem kodu """
        # Arrange
        obj = TestResultParser()
        input_data = '''
Ran 1 tests in 0.001s
OK
Name    Stmts   Miss Branch BrMiss  Cover
-----------------------------------------
leap       26      0      6      0   91%
'''
        # Act
        result = obj.parse(input_data)
        # Assert
        self.assertEqual(result, (1, 0, 0, 91))


@test_type('unit')
class FileMonitorWaitForChangeTestCase(unittest.TestCase):
    """ Test :py:meth:`FileMonitor.wait_for_change`. """

    @patch('tddmon.__main__.time')
    @patch.object(FileMonitor, 'code_has_changed')
    def test_should_raise_exception_on_timeout(self, code_has_changed, time):
        """ Scenariusz: timeout """
        # Arrange
        timeout = 10
        interval = 2
        code_has_changed.side_effect = [False] * (timeout // interval + 1)
        obj = FileMonitor(timeout=timeout, interval=interval)
        # Act
        # Assert
        self.assertRaises(FileMonitorTimeoutError, obj.wait_for_change)

    @patch('tddmon.__main__.time')
    @patch.object(FileMonitor, 'code_has_changed')
    def test_should_return_true_if_code_has_changed(self, code_has_changed, time):
        """ Scenariusz: zmieniony plik """
        # Arrange
        code_has_changed.side_effect = [True]
        obj = FileMonitor()
        # Act
        result = obj.wait_for_change()
        # Assert
        self.assertTrue(result)


@test_type('unit')
class FileMonitorCodeHasChangedTestCase(unittest.TestCase):
    """ Test :py:meth:`FileMonitor.code_has_changed`. """

    @patch.object(FileMonitor, 'file_has_changed')
    @patch.object(FileMonitor, 'get_monitored_files')
    def test_should_return_true_if_code_has_changed(self, get_monitored_files, file_has_changed):
        """ Scenariusz: zmienił się plik """
        # Arrange
        get_monitored_files.side_effect = [['file1.py', 'file2.py']]
        file_has_changed.side_effect = [True]
        obj = FileMonitor()
        # Act
        result = obj.code_has_changed()
        # Assert
        self.assertTrue(result)

    @patch.object(FileMonitor, 'get_monitored_files')
    def test_should_return_false_if_no_files_to_monitor(self, get_monitored_files):
        """ Scenariusz: brak plików """
        # Arrange
        get_monitored_files.side_effect = [[]]
        obj = FileMonitor()
        # Act
        result = obj.code_has_changed()
        # Assert
        self.assertFalse(result)

    @patch.object(FileMonitor, 'file_has_changed')
    @patch.object(FileMonitor, 'get_monitored_files')
    def test_should_return_true_if_some_files_has_changed(self, get_monitored_files, file_has_changed):
        """ Scenariusz: zmienił się plik """
        # Arrange
        get_monitored_files.side_effect = [['file1.py', 'file2.py']]
        file_has_changed.side_effect = [False, True]
        obj = FileMonitor()
        # Act
        result = obj.code_has_changed()
        # Assert
        self.assertTrue(result)


@test_type('unit')
class FileMonitorGetMonitoredFilesTestCase(unittest.TestCase):
    """ Test :py:meth:`FileMonitor.get_monitored_files`. """

    @patch('tddmon.__main__.os.walk')
    def test_should_return_generator_with_files(self, walk):
        """ Scenariusz: generator plików """
        # Arrange
        files_list = [['dir', [], ['file1.py', 'file2.py']]]
        files = ['dir/file1.py', 'dir/file2.py']
        walk.side_effect = [files_list]
        obj = FileMonitor()
        # Act
        result = obj.get_monitored_files()
        # Assert
        self.assertTrue(isinstance(result, types.GeneratorType))
        self.assertEqual(list(result), files)

    @patch('tddmon.__main__.os.walk')
    def test_should_return_filter_out_not_monitored_extensions(self, walk):
        """ Scenariusz: odfiltrowanie niemonitorowanych rozszerzeń """
        # Arrange
        files_list = [['dir', [], ['file1.html', 'file2.py']]]
        files = ['dir/file2.py']
        walk.side_effect = [files_list]
        obj = FileMonitor()
        # Act
        result = obj.get_monitored_files()
        # Assert
        self.assertTrue(isinstance(result, types.GeneratorType))
        self.assertEqual(list(result), files)


@test_type('unit')
class FileMonitorFileHasChagnedTestCase(unittest.TestCase):
    """ Test :py:meth:`FileMonitor.file_has_changed`. """

    def setUp(self):
        self.obj = FileMonitor()
        super(FileMonitorFileHasChagnedTestCase, self).setUp()

    @patch('tddmon.__main__.os.stat')
    def test_should_return_true_if_file_mtime_has_changed(self, stat):
        """ Scenariusz: mtime zmienione """
        # Arrange
        stat().st_mtime = 124
        filename = 'file1.py'
        self.obj._mtimes = {filename: 123}
        # Act
        result = self.obj.file_has_changed(filename)
        # Assert
        self.assertTrue(result)

    @patch('tddmon.__main__.os.stat')
    def test_should_return_false_if_new_file(self, stat):
        """ Scenariusz: mtime zmienione """
        # Arrange
        mtime = 124
        stat().st_mtime = mtime
        filename = 'file1.py'
        # Act
        result = self.obj.file_has_changed(filename)
        # Assert
        self.assertFalse(result)

    @patch('tddmon.__main__.os.stat')
    def test_should_return_false_if_mtime_not_changed(self, stat):
        """ Scenariusz: mtime zmienione """
        # Arrange
        mtime = 124
        stat().st_mtime = mtime
        filename = 'file1.py'
        self.obj._mtimes = {filename: mtime}
        # Act
        result = self.obj.file_has_changed(filename)
        # Assert
        self.assertFalse(result)


@test_type('unit')
class FileMonitorShouldMonitorFileTestCase(unittest.TestCase):
    """ Test :py:meth:`FileMonitor.should_monitor_file`. """

    def test_should_return_false_on_not_monitored_extensions(self):
        """ Scenariusz: niemonitorowane pliki """
        # Arrange
        filename = 'test.py'
        obj = FileMonitor(monitored_extensions=['.html'])
        # Act
        result = obj.should_monitor_file(filename)
        # Assert
        self.assertFalse(result)


@test_type('unit')
class TddMonRunTestCase(unittest.TestCase):
    """ Test :py:meth:`TddMon.run`. """

    def test_should_run_tests_and_display_result(self):
        """ Scenariusz: pojedyncze uruchomienie """
        # Arrange
        stdoutdata = ''
        stderrdata = ''
        status_display = Mock()
        obj = TddMon('test_file.py')
        obj.register(status_display)
        with patch.object(obj, 'test_runner') as test_runner:
            test_runner.run.return_value = (stdoutdata, stderrdata)
            # Act
            obj.run()
            # Assert
            status_display.notify(0, 0, 0, 0)


@test_type('unit')
class TddMonLoopTestCase(unittest.TestCase):
    """ Test :py:meth:`TddMon.loop`. """

    @patch('tddmon.__main__.FileMonitor')
    def test_should_stop_on_keayboard_interrupt(self, FileMonitor):
        """ Scenariusz: przerwanie działania """
        # Arrange
        output = StringIO()
        obj = TddMon('test_file.py', output=output)
        with patch.object(obj, 'run'):
            FileMonitor().wait_for_change.side_effect = [KeyboardInterrupt]
            # Act
            obj.loop()
            # Assert

    @patch('tddmon.__main__.FileMonitor')
    def test_should_run_tests(self, FileMonitor):
        """ Scenariusz: run """
        # Arrange
        obj = TddMon('test_file.py')
        FileMonitor().wait_for_change.side_effect = [True, KeyboardInterrupt]
        # Act
        with patch.object(TddMon, 'run') as run:
            obj.loop()
            # Assert
            run.assert_has_calls([call(), call()])

    @patch('tddmon.__main__.FileMonitor')
    def test_should_notify_with_no_values_on_timeout(self, FileMonitor):
        """ Scenariusz: timeout """
        # Arrange
        output = StringIO()
        obj = TddMon('test_file.py', output=output)
        status_display = Mock()
        obj.register(status_display)
        with patch.object(obj, 'run'):
            with patch.object(obj, 'file_monitor') as file_monitor:
                file_monitor.wait_for_change.side_effect = [FileMonitorTimeoutError, KeyboardInterrupt]
                # Act
                obj.loop()
                # Assert
                status_display.notify.assert_called_once_with(obj, None, None, None, None)


@test_type('unit')
class TddMonRegister(unittest.TestCase):
    """ Test :py:meth:`TddMon.register`. """

    def test_should_register_status_monitor(self):
        """ Scenariusz: rejestracja monitora """
        # Arrange
        monitor = sentinel.monitor
        obj = TddMon('test_file.py')
        self.assertTrue(monitor not in obj._observers)
        # Act
        obj.register(monitor)
        # Assert
        self.assertTrue(monitor in obj._observers)


@test_type('unit')
class RemoteDisplayNotifyTestCase(unittest.TestCase):
    """ Test :py:meth:`RemoteDisplay.notify`. """

    def setUp(self):
        self.output = StringIO()
        self._name = sentinel.name
        self._url = sentinel.url
        self.obj = RemoteDisplay(self._url, self._name)
        super(RemoteDisplayNotifyTestCase, self).setUp()

    @patch('tddmon.__main__.urlopen')
    def test_should_send_status_information(self, urlopen):
        """ Scenariusz: wysyla wynik """
        # Arrange
        # Act
        self.obj.notify(sentinel.observable, sentinel.ran, sentinel.failures,
                        sentinel.errors, sentinel.coverage)
        # Assert
        data = {
            'name': self._name,
            'ran': sentinel.ran,
            'failures': sentinel.failures,
            'errors': sentinel.errors,
            'coverage': sentinel.coverage
        }
        data = urlencode(data)
        urlopen.assert_called_once_with(self._url, data)


if __name__ == '__main__':  # pragma: nobranch
    unittest.main()  # pragma nocover
