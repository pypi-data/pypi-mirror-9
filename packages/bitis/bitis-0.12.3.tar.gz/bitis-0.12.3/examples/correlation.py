#!/usr/bin/python
# .+
# .context    : Binary Timed Signal Processing Library
# .title      : correlation plotting
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
import random

import matplotlib.pyplot as pl

# make repeatable random sequences
random.seed(1)

# create random signals
in_a = bt.noise(-2,-2,12,period_mean=6,width_mean=3)
in_b = bt.noise(-2,-2,12,period_mean=4,width_mean=2)

# compute correlation
corr_ab = in_a.correlation(in_b,step_size=0.1)

# start plotting
fig1 = pl.figure(1,figsize=(5,5))
pl.suptitle('BITIS: correlation of two signals.')

# plot signal a
pl.subplot(3,1,1)
pl.xlim(-2,12)
pl.ylabel('signal a')
pl.xlabel('time')
in_a.plot() 

# plot signal b
pl.subplot(3,1,2)
pl.xlim(-2,12)
pl.ylabel('signal b')
pl.xlabel('time')
in_b.plot() 

# plot correlation function
pl.subplot(3,1,3)
pl.grid()
corr, shift = corr_ab
pl.plot(shift,corr)
pl.ylabel('correlation a b')
pl.xlabel('signal a shift')
pl.subplots_adjust(hspace=0.4)

# save plot to file
fig1.savefig('correlation.png',format='png',)


if __name__ == '__main__':
    pl.show()

#### END
