#!/usr/bin/python
# .+
# .context    : Binary Timed Signal Processing Library
# .title      : graphic and semigraphic plot example
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	29-Sep-2014
# .copyright  :	(c) 2013 Fabrizio Pollastri
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
import locale
import matplotlib.pyplot as pl
import sys
import StringIO as SI

# init locale
locale.setlocale(locale.LC_ALL,"")

# a test signal
signal = bt.test()

# graphic plot
fig1 = pl.figure(1,figsize=(5,2))
pl.suptitle('BITIS: test signal graphic plot.')
pl.xlabel('time')
signal.plot()
pl.grid()

# save graphic plot to file
fig1.savefig('plot.png',format='png')

# sequence of semigraphic plots of increasing resolution
buf = SI.StringIO()
buf.write('BITIS: test signal semigraphic plot\n')
for width in range(1,77,5):
    top, bot = signal.plotchar(width,max_flat=4)
    buf.write('%3d ' % width + top + '\n')
    buf.write('    ' + bot + '\n')
sys.stdout.write(buf.getvalue())

# save semigraphic plot to file
pfile = open('plot.txt','w')
pfile.write(buf.getvalue())
pfile.close()


if __name__ == '__main__':
    pl.show()

#### END
