# -*- coding: utf-8 -*-

# Copyright (c) 2012, Sergio Callegari
# All rights reserved.

# This file is part of PyDSM.

# PyDSM is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# PyDSM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with PyDSM.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division, print_function

import numpy as np
from scipy import signal
import time
from pydsm.NTFdesign import ntf_fir_weighting, quantization_noise_gain
from pydsm.delsig import evalTF
from nose.plugins.skip import SkipTest


class Bench_ntf_fir_weighting(object):

    @classmethod
    def setup_class(cls):
        # signal and filter specification
        fsig = 1000.
        B = 400.
        OSR = 64
        fphi = B*OSR*2
        # Lee constraint
        cls.H_inf = 1.5
        # FIR Order
        cls.order = 25
        w0 = 2*fsig/fphi
        B0 = 2*B/fphi
        w1 = (np.sqrt(B0**2+4*w0**2)-B0)/2
        w2 = (np.sqrt(B0**2+4*w0**2)+B0)/2
        cls.hz = signal.butter(4, [w1, w2], 'bandpass', output='zpk')
        cls.ff = np.linspace(0, 0.5, 1024)

    @classmethod
    def teardown_class(cls):
        pass

    def bench_ntf_fir_weighting_cvxpy_old(self):
        try:
            import cvxpy_tinoco     # analysis:ignore
        except:
            raise SkipTest("Modeler 'cvxpy_old' not installed")
        print("Benchmarking NTF FIR synthesis with 'cvxpy_old' modeler")
        tic = time.clock()
        ntf = ntf_fir_weighting(self.order, self.hz, self.H_inf,
                                modeler='cvxpy_old', show_progress=False)
        timing = time.clock()-tic
        mf = quantization_noise_gain(ntf, self.hz)
        vv = np.abs(evalTF(ntf, np.exp(2j*np.pi*self.ff)))
        pe = np.max(vv)-self.H_inf
        print("Timing: {:6.2f}".format(timing))
        print("Accuracy on constraint: {:e}".format(pe))
        print("Accuracy on goal: {:e}".format(mf))

    def bench_ntf_fir_weighting_cvxpy_cvxopt(self):
        try:
            import cvxpy     # analysis:ignore
        except:
            raise SkipTest("Modeler 'cvxpy' not installed")
        print("Benchmarking NTF FIR synthesis with 'cvxpy' modeler + `cvxopt`")
        tic = time.clock()
        ntf = ntf_fir_weighting(self.order, self.hz, self.H_inf,
                                modeler='cvxpy', show_progress=False)
        timing = time.clock()-tic
        mf = quantization_noise_gain(ntf, self.hz)
        vv = np.abs(evalTF(ntf, np.exp(2j*np.pi*self.ff)))
        pe = np.max(vv)-self.H_inf
        print("Timing: {:6.2f}".format(timing))
        print("Accuracy on constraint: {:e}".format(pe))
        print("Accuracy on goal: {:e}".format(mf))

    def bench_ntf_fir_weighting_cvxpy_cvxopt2(self):
        try:
            import cvxpy     # analysis:ignore
        except:
            raise SkipTest("Modeler 'cvxpy' not installed")
        print("Benchmarking NTF FIR synthesis with 'cvxpy' modeler + `cvxopt`"
              " + default kkt solver")
        tic = time.clock()
        ntf = ntf_fir_weighting(self.order, self.hz, self.H_inf,
                                modeler='cvxpy', show_progress=False,
                                cvxpy_opts={'override_kktsolver': False})
        timing = time.clock()-tic
        mf = quantization_noise_gain(ntf, self.hz)
        vv = np.abs(evalTF(ntf, np.exp(2j*np.pi*self.ff)))
        pe = np.max(vv)-self.H_inf
        print("Timing: {:6.2f}".format(timing))
        print("Accuracy on constraint: {:e}".format(pe))
        print("Accuracy on goal: {:e}".format(mf))

    def bench_ntf_fir_weighting_cvxpy_scs(self):
        try:
            import cvxpy     # analysis:ignore
        except:
            raise SkipTest("Modeler 'cvxpy' not installed")
        print("Benchmarking NTF FIR synthesis with 'cvxpy' modeler + `scs`")
        tic = time.clock()
        ntf = ntf_fir_weighting(self.order, self.hz, self.H_inf,
                                modeler='cvxpy', show_progress=False,
                                cvxpy_opts={'solver': 'scs'})
        timing = time.clock()-tic
        mf = quantization_noise_gain(ntf, self.hz)
        vv = np.abs(evalTF(ntf, np.exp(2j*np.pi*self.ff)))
        pe = np.max(vv)-self.H_inf
        print("Timing: {:6.2f}".format(timing))
        print("Accuracy on constraint: {:e}".format(pe))
        print("Accuracy on goal: {:e}".format(mf))

    def bench_ntf_fir_weighting_picos(self):
        try:
            import picos     # analysis:ignore
        except:
            raise SkipTest("Modeler 'picos' not installed")
        print("Benchmarking NTF FIR synthesis with 'picos' modeler")
        tic = time.clock()
        ntf = ntf_fir_weighting(self.order, self.hz, self.H_inf,
                                modeler='picos', show_progress=False)
        timing = time.clock()-tic
        mf = quantization_noise_gain(ntf, self.hz)
        vv = np.abs(evalTF(ntf, np.exp(2j*np.pi*self.ff)))
        pe = np.max(vv)-self.H_inf
        print("Timing: {:6.2f}".format(timing))
        print("Accuracy on constraint: {:e}".format(pe))
        print("Accuracy on goal: {:e}".format(mf))
