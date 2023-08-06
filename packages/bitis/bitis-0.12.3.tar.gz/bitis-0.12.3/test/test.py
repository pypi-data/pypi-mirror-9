#!/usr/bin/python
# -*- coding: utf-8 -*-
# .+
# .context    : Binary Timed Signal Processing Library
# .title      : Test Suite
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	26-Sep-2013
# .copyright  :	(c) 2013-2014 Fabrizio Pollastri
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
from sys import maxint
import unittest

import matplotlib.pyplot as pl


class TestBitis(unittest.TestCase):

    def setUp(self):
        """ Prepare testing signals """

        # test signal instance
        self.empty = bt.Signal()
        self.test = bt.test()
        self.testing = self.test.clone()

        # test signals: a signal and its shifted copies.
        # Graph of base signal __|^|_|^^^ """
        self.one0 = bt.Signal(0,[],7,slevel=1)
        self.zero0 = bt.Signal(0,[],7)
        self.sig0 = bt.Signal(0,[2,3,4],7)
        self.sig1 = bt.Signal(1,[3,4,5],8)
        self.sig2 = bt.Signal(2,[4,5,6],9)
        self.sig3 = bt.Signal(3,[5,6,7],10)
        self.sig4 = bt.Signal(4,[6,7,8],11)
        self.sig5 = bt.Signal(5,[7,8,9],12)
        self.sig6 = bt.Signal(6,[8,9,10],13)
        self.sig7 = bt.Signal(7,[9,10,11],14)
        self.sig8 = bt.Signal(8,[10,11,12],15)


    def test_level(self):
        """ Test signal level computation. """

        test = bt.Signal(0,[],1)
        self.assertEqual((None,0),test.level(-1))
        self.assertEqual((0,0),test.level(0))
        self.assertEqual((0,0),test.level(0.5))
        self.assertEqual((0,0),test.level(1))
        self.assertEqual((None,0),test.level(2))

        test = bt.Signal(0,[1],2)
        self.assertEqual((None,0),test.level(-1))
        self.assertEqual((0,0),test.level(0))
        self.assertEqual((0,0),test.level(0.5))
        self.assertEqual((0,0),test.level(1))
        self.assertEqual((1,1),test.level(1.5))
        self.assertEqual((1,1),test.level(2))
        self.assertEqual((None,1),test.level(3))

        test = bt.Signal(0,[1,2],3)
        self.assertEqual((None,0),test.level(-1))
        self.assertEqual((0,0),test.level(0))
        self.assertEqual((0,0),test.level(0.5))
        self.assertEqual((0,0),test.level(1))
        self.assertEqual((1,1),test.level(1.5))
        self.assertEqual((1,1),test.level(2))
        self.assertEqual((0,2),test.level(2.5))
        self.assertEqual((0,2),test.level(3))
        self.assertEqual((None,2),test.level(4))

        self.assertEqual((1,1),test.level(0.5,1))
        self.assertEqual((1,1),test.level(1,1))
        self.assertEqual((1,1),test.level(1.5,1))
        self.assertEqual((1,1),test.level(2,1))
        self.assertEqual((0,2),test.level(2.5,1))
        self.assertEqual((0,2),test.level(3,1))
        self.assertEqual((None,2),test.level(4,1))


    def test_clone(self):
        """ Test creation of an identical copy of signal. """

        # compare original test signal and output signal
        self.assertEqual(self.test,self.test.clone())


    def test_shift_inplace(self):
        """ Test inplace signal shifting. """

        # shift forward, backward and to same place again
        self.testing.shift(13)
        self.testing.shift(-23)
        self.testing.shift(10)

        # test expected offsets
        self.assertEqual(self.test,self.testing)


    def test_shift_noinplace(self):
        """ Test not in place signal shifting. """

        # shift forward, backward and to same place again
        testing1 = self.test.shift(13,inplace=False)
        testing2 = testing1.shift(-23,inplace=False)
        testing3 = testing2.shift(10,inplace=False)

        # test expected offsets
        self.assertEqual(self.test,testing3)


    def test_reverse_inplace(self):
        """ Test in place signal edge reversing. """

        # reverse 
        self.testing.reverse(inplace=True)
        self.testing.reverse(inplace=True)

        # compare expected signal and testing result
        self.assertEqual(self.test,self.testing)


    def test_reverse_noinplace(self):
        """ Test not in place signal edge reversing. """

        # reverse 
        testing1 = self.test.reverse(inplace=False)
        testing2 = testing1.reverse(inplace=False)

        # compare expected signal and testing result
        self.assertEqual(self.test,testing2)


    def test_join_split(self):
        """ Make a number of split/join over a random signal.  Test
        equality of original and splitted/joined signal. """

        # make random sequence repeteable
        random.seed(1)

        # test 100 random binary codes sequences
        for s in range(100):

            # build random input data
            start = random.uniform(-100.,100.)
            end = random.uniform(start,start + 10.)
            split = random.uniform(start+0.001,end-0.001)
            period_mean = (end - start) / 100.
            width_mean = 0.2  * period_mean
            inplace = random.randint(0,1)
            original = bt.noise(start,start,end,period_mean=period_mean,
                    width_mean=width_mean)
            if inplace:
              reference = original.clone()
            else:
              reference = original

            # split and join
            signal_a, signal_b = original.split(split,inplace=inplace)
            signal_out = signal_a.join(signal_b)

            # compare original and out signals
            self.assertEqual(reference,signal_out)


    def test_older_newer(self):
        """ Make a number of newer/older splits over a random signal.  Test
        equality of original and splitted/joined signal. """

        # make random sequence repeteable
        random.seed(1)

        # test 100 random binary codes sequences
        for s in range(100):

            # build random input data
            start = random.uniform(-100.,100.)
            end = random.uniform(start,start + 10.)
            split = random.uniform(start+0.001,end-0.001)
            period_mean = (end - start) / 100.
            width_mean = 0.2  * period_mean
            original = bt.noise(start,start,end,period_mean=period_mean,
                    width_mean=width_mean)
            inplace = random.randint(0,1)
            if inplace:
              reference = original.clone()
            else:
              reference = original

            # split and join
            older = original.older(split)
            newer = original.newer(split,inplace=inplace)
            result = older.join(newer)

            # compare original and out signals
            self.assertEqual(reference,result)


    def test_chop_join(self):
        """ Make a number of chop over a random signal.  Test
        equality of original and chopped/joined signal. """

        # make random sequence repeteable
        random.seed(1)

        # test 10 random binary codes sequences
        for s in range(10):

            # build random input data
            start = random.uniform(-100.,100.)
            end = random.uniform(start,start + 100.)
            period_mean = (end - start) / 100.
            width_mean = 0.02  * period_mean
            original = bt.noise(start,start,end,period_mean=period_mean,
                    width_mean=width_mean)

            # chop and join
            chops = original.chop(period_mean,max_chops=200)
            signal_out = chops[0]
            for chop in chops[1:]:
                signal_out.join(chop,inplace=True)

            # compare original and out signals
            self.assertEqual(original,signal_out)


    def test__intersect(self):
        """ Test intersection parameters. """

        testing = self.sig0._intersect(self.sig0)
        self.assertEqual((0,7,0,3,0,0,3,0),testing)
 
        testing = self.sig0._intersect(self.sig1)
        self.assertEqual((1,7,0,3,0,0,3,0),testing)

        testing = self.sig0._intersect(self.sig2)
        self.assertEqual((2,7,0,3,0,0,3,0),testing)

        testing = self.sig0._intersect(self.sig3)
        self.assertEqual((3,7,1,3,1,0,3,0),testing)

        testing = self.sig0._intersect(self.sig4)
        self.assertEqual((4,7,2,3,0,0,2,0),testing)
	 
        testing = self.sig0._intersect(self.sig5)
        self.assertEqual((5,7,3,3,1,0,1,0),testing)

        testing = self.sig0._intersect(self.sig6)
        self.assertEqual((6,7,3,3,1,0,0,0),testing)

        testing = self.sig0._intersect(self.sig7)
        self.assertEqual(None,testing)

        testing = self.sig0._intersect(self.sig8)
        self.assertEqual(None,testing)

        testing = self.sig0._intersect(self.empty)
        self.assertEqual(None,testing)



    def test_invert_inplace(self):
        """ Test in place logical not on test signal. """

        # from original signal to itself through a doble not
        self.testing.__invert__(inplace=True)
        self.testing.__invert__(inplace=True)

        # compare original test signal and output signal
        self.assertEqual(self.test,self.testing)


    def test_invert_noinplace(self):
        """ Test not in place logical not on test signal. """

        # from original signal to itself through a doble not
        testing = ~ ~self.test

        # compare original test signal and output signal
        self.assertEqual(self.test,testing)


    def test_and(self):
        """ Test logical and on test signal. """

        testing = self.sig0 & self.one0
        self.assertEqual(self.sig0,testing)

        testing = self.sig0 & self.sig0
        self.assertEqual(self.sig0,testing)

        testing = self.sig0 & self.sig1
        expected = bt.Signal(1,[5],7,slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 & self.sig2
        expected = bt.Signal(2,[4,5,6],7,slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 & self.sig3
        expected = bt.Signal(3,[5,6,7],7,slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 & self.sig4
        expected = bt.Signal(4,[6,7],7,slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 & self.sig5
        expected = bt.Signal(5,[7],7,slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 & self.sig6
        expected = bt.Signal(6,[],7,slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 & self.sig7
        expected = bt.Signal()
        self.assertEqual(expected,testing)

    
    def test_or(self):
        """ Test logical or on test signal. """

        testing = self.sig0 | self.sig0
        self.assertEqual(self.sig0,testing)

        testing = self.sig0 | self.sig1
        expected = bt.Signal(1,[2],7,slevel=0,tscale=1)
        self.assertEqual(expected,testing)
 
        testing = self.sig0 | self.sig2
        expected = bt.Signal(2,[2,3,4],7,slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 | self.sig3
        expected = bt.Signal(3,[3,4],7,slevel=1,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 | self.sig4
        expected = bt.Signal(4,[4],7,slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 | self.sig5
        expected = bt.Signal(5,[],7,slevel=1,tscale=1)
        self.assertEqual(expected,testing)


    def test_xor(self):
        """ Test logical xor on test signal. """

        testing = self.sig0 ^ self.sig0
        expected = bt.Signal(0,[],7,slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 ^ self.sig1
        expected = bt.Signal(1,[2,5],7,slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 ^ self.sig2
        expected = bt.Signal(2,[2,3,5,6],7,slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 ^ self.sig3
        expected = bt.Signal(3,[3,4,5,6,7],7,slevel=1,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 ^ self.sig4
        expected = bt.Signal(4,[4,6,7],7,slevel=0,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 ^ self.sig5
        expected = bt.Signal(5,[7],7,slevel=1,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 ^ self.sig6
        expected = bt.Signal(6,[],7,slevel=1,tscale=1)
        self.assertEqual(expected,testing)

        testing = self.sig0 ^ self.sig7
        expected = bt.Signal()
        self.assertEqual(expected,testing)


    def test_logic(self):
        """ Test signal logic functions by computing the xor of two
        signals in two ways. The first, directly by xor method. The
        second using the equation a xor b = a and not b or not a and b.
        Signal times are floats. """

        # make repeatable random sequences
        random.seed(1)

        # iterate test on several random signals
        for t in range(20):

            # create random signals
            start_a = random.uniform(-100.,100.)
            end_a = random.uniform(start_a,start_a + 100.)
            start_b = (start_a + end_a) / 2.
            end_b = random.uniform(start_b,start_b + 100.)
            in_a = bt.noise(start_a,start_a,end_a,period_mean=0.1,width_mean=3)
            in_b = bt.noise(start_b,start_b,end_b,period_mean=0.3,width_mean=2)

            in_a = self.sig0
            in_b = self.sig2

            # direct xor
            xor1 = in_a ^ in_b

            # xor from equation
            xor2 = in_a & ~in_b | ~in_a & in_b

            # compare original test signal and output signal
            self.assertEqual(xor1,xor2)



    def test_integral(self):
        """ Test integral of signal computation. """

        self.assertEqual(30,self.test.integral(1))
        self.assertEqual(33,self.test.integral(0))
        self.assertEqual(33,(~self.test).integral(1))
        self.assertEqual(30,(~self.test).integral(0))


    def test_correlation(self):
        """ Test correlation function of two signals (*self* and *other*). """

        # create test signals
        in_a = bt.Signal(-2,[-1,1,2,7],12)
        in_b = bt.Signal(-2,[0,3,5,8],12)
        expected_corr =  [ 1., 2., 2., 2.,2.,2.,2.,3.,4.,5.,6.,6.,6.]
        expected_times = [-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1]
        expected_corr +=  [9.,10.,9.,7.,3.,3.,3.,3.,2.,1.,2.,1.,1.,1.]
        expected_times += [0,1,2,3,4,5,6,7,8,9,10,11,12,13]

        # test, no skip, no width.
        corr, times = in_a.correlation(in_b)
        self.assertEqual(expected_corr,corr)
        self.assertEqual(expected_times,times)

        # test, with skip, no width.
        corr, times = in_a.correlation(in_b,skip=1.)
        self.assertEqual(expected_corr[1:],corr)
        self.assertEqual(expected_times[1:],times)
        corr, times = in_a.correlation(in_b,skip=2.)
        self.assertEqual(expected_corr[2:],corr)
        self.assertEqual(expected_times[2:],times)
        corr, times = in_a.correlation(in_b,skip=26.)
        self.assertEqual(expected_corr[26:],corr)
        self.assertEqual(expected_times[26:],times)
        corr, times = in_a.correlation(in_b,skip=27.)
        self.assertEqual(expected_corr[27:],corr)
        self.assertEqual(expected_times[27:],times)
        corr, times = in_a.correlation(in_b,skip=28.)
        self.assertEqual(expected_corr[28:],corr)
        self.assertEqual(expected_times[28:],times)

        # test, with width, no skip.
        corr, times = in_a.correlation(in_b,width=-1.)
        self.assertEqual([],corr)
        self.assertEqual([],times)
        corr, times = in_a.correlation(in_b,width=1.)
        self.assertEqual(expected_corr[:1],corr)
        self.assertEqual(expected_times[:1],times)
        corr, times = in_a.correlation(in_b,width=2.)
        self.assertEqual(expected_corr[:2],corr)
        self.assertEqual(expected_times[:2],times)
        corr, times = in_a.correlation(in_b,width=27.)
        self.assertEqual(expected_corr,corr)
        self.assertEqual(expected_times,times)
        corr, times = in_a.correlation(in_b,width=28.)
        self.assertEqual(expected_corr,corr)
        self.assertEqual(expected_times,times)

        # test, with skip and width.
        corr, times = in_a.correlation(in_b,skip=1.,width=1.)
        self.assertEqual(expected_corr[1:2],corr)
        self.assertEqual(expected_times[1:2],times)
        corr, times = in_a.correlation(in_b,skip=5.,width=10.)
        self.assertEqual(expected_corr[5:15],corr)
        self.assertEqual(expected_times[5:15],times)
        corr, times = in_a.correlation(in_b,skip=25.,width=1.)
        self.assertEqual(expected_corr[25:26],corr)
        self.assertEqual(expected_times[25:26],times)
        corr, times = in_a.correlation(in_b,skip=26.,width=1.)
        self.assertEqual(expected_corr[26:27],corr)
        self.assertEqual(expected_times[26:27],times)


    def test_phase(self):
        """ Test phase function of two signals (*self* and *other*). """

        # make random sequence repeteable
        random.seed(1)

        # create random test signals
        model = bt.noise(0.,0.,10.,period_mean=2,period_stddev=0.5,
            width_mean=1,width_stddev=0.25,active=1)
        base = bt.noise(-10.,-10.,10.,period_mean=1,period_stddev=0.25,
            width_mean=0.25,width_stddev=0.125,active=1)

        # apply a sliding phase to sig, add base and compute phase from model
        for i in range(10):
            expected_phase = random.uniform(0.,10.)
            #expected_phase = 2.49
            ssig = model.shift(-expected_phase,inplace=False)
            ssig.start = -10.
            ssig.end = +10.
            ssig = ssig | base
            phase, corr_phase, corrs, shifts = \
                ssig.phase(model,None,(0.5,0.1,0.01))

            # test detected phase
            self.assertAlmostEqual(expected_phase,phase,delta=0.01)


    def test_plotchar(self):
        """ Test semigraphic plotting. """

        top, bot = bt.Signal(0,[],1).plotchar(3,-1,2)
        self.assertEqual('   ',top)
        self.assertEqual(' ─ ',bot)
        top, bot = bt.Signal(0,[1],2).plotchar(4,-1,3)
        self.assertEqual('  ┌ ',top)
        self.assertEqual(' ─┘ ',bot)

        top, bot = bt.Signal(0,[],1).plotchar(3,0.1,0.4)
        self.assertEqual('   ',top)
        self.assertEqual('───',bot)

        top, bot = bt.Signal(0,[1,2],3).plotchar(1)
        self.assertEqual('╻',top)
        self.assertEqual('┸',bot)
        top, bot = bt.Signal(0,[1,2],3).plotchar(2)
        self.assertEqual('┌┐',top)
        self.assertEqual('┘└',bot)
        top, bot = bt.Signal(0,[1,2],3).plotchar(3)
        self.assertEqual(' ┌┐',top)
        self.assertEqual('─┘└',bot)
        top, bot = bt.Signal(0,[1,2],3).plotchar(4)
        self.assertEqual(' ┌┐ ',top)
        self.assertEqual('─┘└─',bot)

        top, bot = bt.Signal(0,[1,2,3],4).plotchar(1)
        self.assertEqual('┎',top)
        self.assertEqual('┚',bot)
        top, bot = bt.Signal(0,[1,2,3],4).plotchar(2)
        self.assertEqual('┌┰',top)
        self.assertEqual('┘╹',bot)
        top, bot = bt.Signal(0,[1,2,3],4).plotchar(3)
        self.assertEqual('┌┐┌',top)
        self.assertEqual('┘└┘',bot)
        top, bot = bt.Signal(0,[1,2,3],4).plotchar(4)
        self.assertEqual(' ┌┐┌',top)
        self.assertEqual('─┘└┘',bot)
        top, bot = bt.Signal(0,[1,2,3],4).plotchar(5)
        self.assertEqual(' ┌┐┌─',top)
        self.assertEqual('─┘└┘ ',bot)
        top, bot = bt.Signal(0,[1,2,3],4).plotchar(6)
        self.assertEqual(' ┌─┐┌─',top)
        self.assertEqual('─┘ └┘ ',bot)
        top, bot = bt.Signal(0,[1,2,3],4).plotchar(7)
        self.assertEqual(' ┌─┐ ┌─',top)
        self.assertEqual('─┘ └─┘ ',bot)

        top, bot = bt.Signal(0,[1,2],4).plotchar(4,max_flat=4)
        self.assertEqual(' ┌┐ ',top)
        self.assertEqual('─┘└─',bot)
        top, bot = bt.Signal(0,[1,2],4).plotchar(5,max_flat=4)
        self.assertEqual(' ┌┐  ',top)
        self.assertEqual('─┘└──',bot)
        top, bot = bt.Signal(0,[1,2],4).plotchar(6,max_flat=4)
        self.assertEqual(' ┌─┐  ',top)
        self.assertEqual('─┘ └──',bot)
        top, bot = bt.Signal(0,[1,2],4).plotchar(7,max_flat=4)
        self.assertEqual(' ┌─┐   ',top)
        self.assertEqual('─┘ └───',bot)
        top, bot = bt.Signal(0,[1,2],4).plotchar(8,max_flat=4)
        self.assertEqual('  ┌─┐   ',top)
        self.assertEqual('──┘ └───',bot)
        top, bot = bt.Signal(0,[1,2],4).plotchar(9,max_flat=4)
        self.assertEqual('  ┌─┐    ',top)
        self.assertEqual('──┘ └────',bot)
        top, bot = bt.Signal(0,[1,2],4).plotchar(10,max_flat=4)
        self.assertEqual('  ┌──┐    ',top)
        self.assertEqual('──┘  └────',bot)
        top, bot = bt.Signal(0,[1,2],4).plotchar(11,max_flat=4)
        self.assertEqual('  ┌──┐    ',top)
        self.assertEqual('──┘  └──x─',bot)
        top, bot = bt.Signal(0,[1,2],4).plotchar(12,max_flat=4)
        self.assertEqual('   ┌──┐    ',top)
        self.assertEqual('───┘  └──x─',bot)
        top, bot = bt.Signal(0,[1,2],4).plotchar(13,max_flat=4)
        self.assertEqual('   ┌──┐    ',top)
        self.assertEqual('───┘  └──x─',bot)
        top, bot = bt.Signal(0,[1,2],4).plotchar(14,max_flat=4)
        self.assertEqual('   ┌───┐    ',top)
        self.assertEqual('───┘   └──x─',bot)
        top, bot = bt.Signal(0,[1,2],4).plotchar(15,max_flat=4)
        self.assertEqual('   ┌───┐    ',top)
        self.assertEqual('───┘   └──x─',bot)
        top, bot = bt.Signal(0,[1,2],4).plotchar(19,max_flat=4)
        self.assertEqual('    ┌────┐    ',top)
        self.assertEqual('────┘    └──x─',bot)
        top, bot = bt.Signal(0,[1,2],4).plotchar(20,max_flat=4)
        self.assertEqual('    ┌────┐    ',top)
        self.assertEqual('──x─┘    └──x─',bot)
        top, bot = bt.Signal(0,[1,2],4).plotchar(21,max_flat=4)
        self.assertEqual('    ┌────┐    ',top)
        self.assertEqual('──x─┘    └──x─',bot)
        top, bot = bt.Signal(0,[1,2],4).plotchar(22,max_flat=4)
        self.assertEqual('    ┌──x─┐    ',top)
        self.assertEqual('──x─┘    └──x─',bot)

        top, bot = self.test.plotchar(1,max_flat=4)
        self.assertEqual('╻',top)
        self.assertEqual('┸',bot)
        top, bot = self.test.plotchar(6,max_flat=4)
        self.assertEqual('╻╻╻╻┎┒',top)
        self.assertEqual('┸┸┸┸┚┖',bot)
        top, bot = self.test.plotchar(11,max_flat=4)
        self.assertEqual('╻╻╻╻┌┰┐╻┌┐╻',top)
        self.assertEqual('┸┸┸┸┘╹└┸┘└┸',bot)
        top, bot = self.test.plotchar(16,max_flat=4)
        self.assertEqual('┎┰┐╻┌┐┌┐┌┐┌┐┌┐ ╻',top)
        self.assertEqual('┚╹└┸┘└┘└┘└┘└┘└─┸',bot)



    def test_pwm_codec_noperiod(self):
        """ Make a number of conversion from a random code to the
        corresponding pwm signal and back again to code. Test
        equality of input and output codes. Use pulse elapse
        conversion method. """

        # make random sequence repeteable
        random.seed(1)

        # teist 100 random binary codes sequences
        for s in range(100):

            # build random input data
            bit_length = random.randint(0,32)
            code = random.randint(-maxint-1,maxint)
            code_in = (bit_length,code)
            period = random.randint(10,20)
            elapse_0 = random.randint(1,2)
            elapse_1 = random.randint(1,2) + elapse_0
            active = random.randint(0,1)
            origin = random.uniform(-100.,100.)

            # clear unused code bits into code_in
            mask = 0
            for i in range(code_in[0]):
                mask <<= 1
                mask |= 1
            code_in = (code_in[0],code_in[1] & mask)

            # from codes to pulses and back again
            pwm = bt.bin2pwm(code_in,elapse_0,elapse_1,period,active,origin)
            code_out = bt.pwm2bin(pwm,elapse_0,elapse_1)

            # compare in and out codes
            self.assertEqual(code_in,code_out)


    def test_pwm_codec_period(self):
        """ Make a number of conversion from a random code to the
        corresponding pwm signal and back again to code. Test
        equality of input and output codes. Use pulse correlation
        conversion method. """

        # make random sequence repeteable
        random.seed(1)

        # test 100 random binary codes sequences
        for s in range(100):

            # build random input data
            bit_length = random.randint(0,32)
            code = random.randint(-maxint-1,maxint)
            code_in = (bit_length,code)
            period = random.randint(10,20)
            elapse_0 = random.randint(1,2)
            elapse_1 = random.randint(1,2) + elapse_0
            active = random.randint(0,1)
            origin = random.uniform(-100.,100.)

            # clear unused code bits into code_in
            mask = 0
            for i in range(code_in[0]):
                mask <<= 1
                mask |= 1
            code_in = (code_in[0],code_in[1] & mask)

            # from codes to pulses and back again
            pwm = bt.bin2pwm(code_in,elapse_0,elapse_1,period,active,origin)
            code_out, error = bt.pwm2bin(pwm,elapse_0,elapse_1,period,active)

            # compare in and out codes
            self.assertEqual(0,error)
            self.assertEqual(code_in,code_out)


    def test_serial_tx_rx(self):
        """ Simulate encode and decode of a list of chars over a serial line.
        Test the equality of the original char list with the received one. """

        # constants
        parity_keys = ['off','odd','even']

        # make random sequence repeteable
        random.seed(1)

        # make whole test 10 time
        for j in range(10):

            # make random serial parameters
            char_bits = random.randint(7,8)
            parity = parity_keys[random.randint(0,2)]
            stop_bits = random.randint(1,2)

            # make random chars and timings
            chars_in = []
            timings_in = []
            start = 0
            for i in range(10):
                chars_in.append(chr(random.randint(0,2**char_bits-1)))
                start += abs(int(random.gauss(0,500))) + 240
                timings_in.append(start)

            # transmit and receive
            sline = bt.serial_tx(chars_in,timings_in,char_bits=char_bits,
                    parity=parity,stop_bits=stop_bits)
            chars_out, timings_out, status = bt.serial_rx(sline,
                    char_bits=char_bits,parity=parity,stop_bits=stop_bits)

            # compare in and out chars, theirs timings and test for ok status
            self.assertEqual(zip(chars_in,timings_in),
                   zip(chars_out,timings_out))
            self.assertTrue(all([s == 0 for s in status]))


    def test_code_modem(self):
        """ Simulate encode and decode with symbol modulation and correlation.
        Test the equality of the original code and the demodulated one. """

        # make random sequence repeteable
        random.seed(1)

        # make whole test 20 time
        for j in range(20):

            # build random symbols
            start = 0.
            end =  4.
            period_mean = (end - start) / 100.
            width_mean = 0.2  * period_mean
            symbols_num = random.randint(2,10)
            symbols = []
            for i in range(symbols_num):
                symbol = bt.noise(start,start,end,period_mean=period_mean,
                    width_mean=width_mean)
                # ensure same start and end levels equal to 0
                while symbol.slevel or symbol.slevel != symbol.end_level():
                    symbol = bt.noise(start,start,end,period_mean=period_mean,
                        width_mean=width_mean)
                symbols.append(symbol)

            # build random code
            code_len = random.randint(1,20)
            code = []
            for i in range(code_len):
                code.append(random.randint(0,symbols_num-1))

            # modulate and demodulate
            mod = bt.code2mod(code,symbols)
            decode, corr, corrs = bt.mod2code(mod,symbols)

            # compare in and out chars, theirs timings and test for ok status
            self.assertEqual(code,decode)


    def test_stream(self):
        """ Divide a signal in several chunks by subsequent splits. Pass them
        to a stream signal. Save stream excess into an accumulator. Compare
        at each split the original signal with the concatenation of
        accumulator, stream and most recent part of the last split. """
        
        # make random sequence repeteable
        random.seed(1)

        # create signals
        start = 0
        end =200 
        original = bt.noise(start,start,end)
        stream = bt.Signal()
        accumulator = bt.Signal()

        # split original several times, pass first splited part to a stream
        # signal, append stream excess to an accumulator signal.
        # At each step, check if original is equal to part b + stream + acc.
        tosplit = original
        for i in range(10):
            start = tosplit.start
            split = random.uniform(start,end)
            part_a, part_b = tosplit.split(split)
            tosplit = part_b
            excess, stream = stream.stream(part_a,30)
            accumulator.append(excess)
            result = accumulator + stream + part_b
            self.assertEqual(original,accumulator + stream + part_b)


# main

if __name__ == '__main__':
    unittest.main()

#### END
