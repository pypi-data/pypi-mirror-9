#!/usr/bin/python
# .+
# .context    : Binary Timed Signal Processing Library
# .title      : direct xor vs computed xor
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	28-Oct-2013
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

## Check the equation: a xor b = a and not b  or  not a and b

# create two random signals
a = bt.noise(0,0,100,period_mean=10,width_mean=3)
b = bt.noise(-10,-10,90,period_mean=4,width_mean=2)

# direct xor
xor1 = a ^ b

# xor from equation
xor2 = a & ~b | ~a & b

# check results
if xor1 == xor2:
    print 'Success!'
else:
    print 'Failure!'
        
#### END
