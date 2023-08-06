#!/usr/bin/python
# .+
# .context    : Binary Timed Signal Processing Library
# .title      : serial tx plotting
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	2-Nov-2013
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
import matplotlib.pyplot as pl

CHAR_BITS = 8
PARITY = 'odd'
STOP_BITS = 2
BAUD = 50
TSCALE = 1.

chars = ['U']
timings = [0]

fig1 = pl.figure(1,figsize=(5,2))
pl.suptitle('BITIS: "U" character serial line coding.')
pl.xlabel('time')
bt.serial_tx(chars,timings,char_bits=CHAR_BITS,parity=PARITY,
        stop_bits=STOP_BITS,baud=BAUD).plot()
bit_time = TSCALE / BAUD
pl.text(bit_time/2,0.5,'S',ha='center')
mask = 1
for c in range(CHAR_BITS):
    if ord(chars[0]) & mask:
        char = '1'
    else:
        char = '0'
    pl.text((c + 1.5) * bit_time,0.5,char,ha='center')
    mask <<= 1
pl.text((c + 2.5) * bit_time,0.5,'P',ha='center')
pl.text((c + 3.5) * bit_time,0.5,'E',ha='center')
pl.text((c + 4.5) * bit_time,0.5,'E',ha='center')
pl.grid()

# save plot to file
fig1.savefig('serial_tx.png',format='png')


if __name__ == '__main__':
    pl.show()

#### END
