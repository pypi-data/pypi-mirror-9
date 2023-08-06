#!/usr/bin/python
# .+
# .context    : Binary Timed Signal Processing Library
# .title      : Examples Test Suite
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	24-Sep-2014
# .copyright  :	(c) 2014 Fabrizio Pollastri
# .license    : GNU General Public License (see below)
#
# This file is part of "BITIS, Binary Timed Signal Processing Library".
#
# BITIS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# BITIS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software. If not, see <http://www.gnu.org/licenses/>.
#
# .-


import bitis as bt
import matplotlib.pyplot as pl
import StringIO as st
import sys
import time as tm
import unittest


class TestBitisExamples(unittest.TestCase):

    def setUp(self):
        """ Redirect output of tested script to test suite. """
        self.output = st.StringIO()
        self.saved_stdout = sys.stdout
        sys.stdout = self.output
        pl.ion()


    def tearDown(self):
        """ retore standard output. """
        self.output.close()
        sys.stdout = self.saved_stdout


    def test_correlation(self):

        import examples.correlation

        pl.show()
        tm.sleep(2)
        pl.close()

        self.assertEqual(self.output.getvalue(),'')


    def test_lockin(self):

        import examples.lockin

        pl.show()
        tm.sleep(2)
        pl.close()

        self.assertEqual(self.output.getvalue(),'')


    def test_serial_tx(self):

        import examples.serial_tx

        pl.show()
        tm.sleep(2)
        pl.close()

        self.assertEqual(self.output.getvalue(),'')


    def test_xor(self):

        import examples.xor_logic

        self.assertEqual(self.output.getvalue(),'Success!\n')


# main

if __name__ == '__main__':
    unittest.main()

#### END
