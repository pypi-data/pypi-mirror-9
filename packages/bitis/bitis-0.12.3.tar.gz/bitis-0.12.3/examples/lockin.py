#!/usr/bin/python
# .+
# .context    : Binary Timed Signal Processing Library
# .title      : lockin plotting
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	7-Dec-2013
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

# generate the original signal: square wave, 50 cycles @1Hz, 50% duty cycle.
original = bt.square(0.,0.,50.,1.,0.5)

# add jitter to original signal
jittered = original.clone()
jittered.jitter(0.1)

# add noise by xor
jittered_noised = jittered ^ bt.noise(0,0,50,period_mean=5,width_mean=0.5)

# compute correlation between original and disturbed signal
corr, shift = original.correlation(jittered_noised,step_size=0.05,
    skip=49.45,width=1.05)

# start plotting
fig1 = pl.figure(1,figsize=(6,7))
pl.suptitle('BITIS: lockin to a noisy signal.')

# plot original signal
pl.subplot(4,1,1)
pl.xlim(-1,51)
pl.ylabel('original')
pl.xlabel('time')
original.plot() 

# plot signal with jitter
pl.subplot(4,1,2)
pl.xlim(-1,51)
pl.ylabel('+jitter')
pl.xlabel('time')
jittered.plot() 

# plot signal with jitter and noise
pl.subplot(4,1,3)
pl.xlim(-1,51)
pl.ylabel('+noise+jitter')
pl.xlabel('time')
jittered_noised.plot() 

# plot correlation function
pl.subplot(4,1,4)
pl.grid()
pl.plot(shift,corr)
pl.ylabel('correlation')
pl.xlabel('lockin phase')
pl.subplots_adjust(hspace=0.4)

# save plot to file
fig1.savefig('lockin.png',format='png')


if __name__ == '__main__':
    pl.show()

#### END
