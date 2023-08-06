#!/usr/bin/python
# .+
# .context    : Binary Timed Signal Processing Library
# .title      : modulation  and demodulation example
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
import random
import matplotlib.pyplot as pl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

SYMBOLS_NUM = 4
SYMBOL_ELAPSE = 4.
SYMBOL_PULSES_MEAN_PERIOD = 1.
SYMBOL_PULSES_MEAN_WIDTH = 0.5
CODE = [3,0,1,2]

# make repeatable random sequences
random.seed(1)

# generate symbols as random signals
symbols = []
for i in range(SYMBOLS_NUM):
    symbol = bt.noise(0.,SYMBOL_ELAPSE,period_mean=
        SYMBOL_PULSES_MEAN_PERIOD,width_mean=SYMBOL_PULSES_MEAN_WIDTH)
    # ensure same start and end levels equal to 0
    while symbol.slevel or symbol.slevel != symbol.end_level():
        symbol = bt.noise(0.,SYMBOL_ELAPSE,period_mean=
            SYMBOL_PULSES_MEAN_PERIOD,width_mean=SYMBOL_PULSES_MEAN_WIDTH)
    symbols.append(symbol)

# modulate
mod = bt.code2mod(CODE,symbols)

# demodulate
decode, corr, corrs = bt.mod2code(mod,symbols)
        
# plot symbols
fig1 = pl.figure(1,figsize=(6,6))
pl.suptitle('BITIS: modulation symbols.')
for i in range(len(symbols)):
    pl.subplot(4,1,i+1)
    pl.xlim(0,SYMBOL_ELAPSE)
    pl.ylabel('%d symbol' % i)
    pl.xlabel('time')
    symbols[i].plot() 

# plot modulated signal
fig2 = pl.figure(2,figsize=(6,2.5))
fig2.subplots_adjust(top=0.9,bottom=0.2)
pl.suptitle('BITIS: modulated signal.')
pl.xlim(0,SYMBOL_ELAPSE*len(CODE))
pl.xlabel('time')
pl.xticks(np.arange(0,17,4))
pl.grid(axis='x',linestyle='-',linewidth=1)
mod.plot()
for c in range(len(CODE)):
    pl.text(c*4+2 ,0.5,'code %d' % CODE[c],ha='center',size=14)

# plot correlation matrix of modulated signal
fig3 = pl.figure(3,figsize=(6,6))
pl.suptitle('BITIS: correlation matrix of modulated signal.')
ax = fig3.gca(projection='3d')
x, y = np.mgrid[0:len(CODE),0:SYMBOLS_NUM] - 0.1
x = x.flatten()
y = y.flatten()
z = np.zeros_like(x)
pl.xlabel('code time')
pl.ylabel('symbol')
ax.set_zlabel('correlation')
dz = np.array(corrs).flatten()
pl.xticks(np.arange(4))
pl.yticks(np.arange(4))
cz = ['g']*len(z)
for i in range(len(cz)):
    if dz[i] > 0.9:
        cz[i] = 'r'
ax.bar3d(x,y,z,0.2,0.2,dz,color=cz)

# save plots to files
fig1.savefig('modem1.png',format='png')
fig2.savefig('modem2.png',format='png')
fig3.savefig('modem3.png',format='png')


if __name__ == '__main__':
    pl.show()

#### END
