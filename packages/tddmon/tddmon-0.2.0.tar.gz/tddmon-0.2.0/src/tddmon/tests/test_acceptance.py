# -*- coding: utf-8 -*-
import re
import unittest

from mock import patch
from morelia import Parser
from six.moves import StringIO
from smarttest.decorators import test_type

from tddmon import DEFAULT_COLORS, TddMon, ColorDisplay


@test_type('acceptance')
class RunMonitorTestCase(unittest.TestCase):
    " Testy akceptacyjne przypadku: uruchamiam testy "

    feature = 'docs/features/uruchamiam_testy.feature'

    def step_monitorowane_sa_pliki(self, monitored_files):
        u'monitorowane są pliki "([^"]+)"'

        self.monitored_files = monitored_files

    def step_plik_testow_zawiera_num_testow(self, test_file, tests_num):
        u'plik "([^"]+)" zawiera (.+) testów'

        self.test_file = test_file
        self.tests_num = int(tests_num)
        self.output = StringIO()
        self.controller = TddMon(self.test_file)
        self.status_display = ColorDisplay(self.output)
        self.controller.register(self.status_display)

    def step_failures_num_testow_skutkuje_niepowodzeniem(self, failures_num):
        u'(.+) testów skutkuje niepowodzeniem'

        self.failures_num = int(failures_num)

    def step_errors_num_testow_skutkuje_bedem(self, errors_num):
        u'(.+) testów skutkuje błędem'

        self.errors_num = int(errors_num)

    def step_coverage_procent_kodu_pokryte_jest_testami(self, coverage):
        u'(.+) procent kodu pokryte jest testami'

        self.coverage = int(coverage)

    def step_zmienie_plik(self, modified_file):
        u'zmienię plik "([^"]+)"'

        self.modified_file = modified_file

    @patch('tddmon.subprocess.Popen')
    def step_wykona_sie_test(self, Popen):
        u'wykona się test'
        if self.failures_num or self.errors_num:
            failures = []
            if self.failures_num:
                failures.append('failures=%d' % self.failures_num)
            if self.errors_num:
                failures.append('errors=%d' % self.errors_num)
            status = 'FAILED (%s)' % (', '.join(failures))
        else:
            status = 'OK'
        stderrdata = 'Ran %d test in 0.038s\n\n%s\n' % (self.tests_num, status)
        test_result = ('', stderrdata)
        stdoutdata = 'TOTAL 1619 750 584 405 %d%%\n' % self.coverage
        coverage_result = (stdoutdata, '')
        Popen().communicate.side_effect = [test_result, coverage_result]

        self.controller.run()

    def step_zobacze_na_czerwono_informacje_o_wykonaniu_testow(self, tests_num):
        u'zobaczę na czerwono informację o wykonaniu (.+) testów'

        color = DEFAULT_COLORS['red']
        expected = '^\033\[%sm\s+%d' % (color, int(tests_num))
        result = self.output.getvalue().splitlines()[-1]
        self.assertTrue(bool(re.search(expected, result)))

    def step_zobacze_na_czerwono_informacje_o_failures_num_testach_zakonczonych_niepowodzeniem(self, failures_num):
        u'zobaczę na czerwono informację o (.+) testach zakończonych niepowodzeniem'

        color = DEFAULT_COLORS['red']
        expected = '^\033\[%sm\s+\d+\s+%d' % (color, int(failures_num))
        result = self.output.getvalue().splitlines()[-1]
        self.assertTrue(bool(re.search(expected, result)))

    def step_zobacze_na_czerwono_informacje_o_errors_num_testach_zakonczonych_bedem(self, errors_num):
        u'zobaczę na czerwono informację o (.+) testach zakończonych błędem'

        color = DEFAULT_COLORS['red']
        expected = '^\033\[%sm\s+\d+\s+\d+\s+%d' % (color, int(errors_num))
        result = self.output.getvalue().splitlines()[-1]
        self.assertTrue(bool(re.search(expected, result)))

    def step_zobacze_na_czerwono_informacje_o_pokryciu_kodu_na_poziomie_coverage(self, coverage):
        u'zobaczę na czerwono informację o pokryciu kodu na poziomie (.+)'

        color = DEFAULT_COLORS['red']
        expected = '^\033\[%sm\s+\d+\s+\d+\s+\d+\s+%d' % (color, int(coverage))
        result = self.output.getvalue().splitlines()[-1]
        self.assertTrue(bool(re.search(expected, result)))

    def step_wszystkie_testy_przechodza(self):
        u'wszystkie testy przechodzą'

        self.failures_num = 0
        self.errors_num = 0

    def step_zobacze_na_zielono_informacje_o_wykonaniu_tests_num_testow(self, tests_num):
        u'zobaczę na zielono informację o wykonaniu (.+) testów'

        color = DEFAULT_COLORS['green']
        expected = '^\033\[%sm\s+%d' % (color, int(tests_num))
        result = self.output.getvalue().splitlines()[-1]
        self.assertTrue(bool(re.search(expected, result)))

    def step_zobacze_na_zielono_informacje_o_pokryciu_kodu_na_poziomie_coverage(self, coverage):
        u'zobaczę na zielono informację o pokryciu kodu na poziomie (.+)'

        color = DEFAULT_COLORS['green']
        expected = '^\033\[%sm\s+\d+\s+\d+\s+\d+\s+%d' % (color, int(coverage))
        result = self.output.getvalue().splitlines()[-1]
        self.assertTrue(bool(re.search(expected, result)))

    def step_zobacze_w_kolorze_morskim_informacje_o_pokryciu_kodu_na_poziomie_coverage(self, coverage):
        u'zobaczę w kolorze morskim informację o pokryciu kodu na poziomie (.+)'

        color = DEFAULT_COLORS['sea']
        expected = '^\033\[\d+m\s+\d+\s+\d+\s+\d+\033\[%sm\s*%d' % (color, int(coverage))
        result = self.output.getvalue().splitlines()[-1]
        self.assertTrue(bool(re.search(expected, result)))

    def step_poprzedni_test_zakonczy_sie_sukcesem(self):
        u'poprzedni test zakończył się sukcesem'

        self.status_display._last_run_color = DEFAULT_COLORS['green']

    def step_zobacze_na_niebiesko_informacje_o_wykonaniu_tests_num_testow(self, tests_num):
        u'zobaczę na niebiesko informację o wykonaniu (.+) testów'

        color = DEFAULT_COLORS['blue']
        expected = '^\033\[%sm\s+%d' % (color, int(tests_num))
        result = self.output.getvalue().splitlines()[-1]
        self.assertTrue(bool(re.search(expected, result)))

    def step_zobacze_na_niebiesko_informacje_o_pokryciu_kodu_na_poziomie_coverage(self, coverage):
        u'zobaczę na niebiesko informację o pokryciu kodu na poziomie (.+)'

        color = DEFAULT_COLORS['blue']
        expected = '^\033\[%sm\s+\d+\s+\d+\s+\d+\s+%d' % (color, int(coverage))
        result = self.output.getvalue().splitlines()[-1]
        self.assertTrue(bool(re.search(expected, result)))

    def test_run_tests(self):
        " Właściwość: Uruchamiam testy "
        Parser().parse_file(self.feature).evaluate(self)


if __name__ == '__main__':  # pragma: nobranch
    unittest.main()  # pragma nocover
