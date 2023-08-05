# -*- coding: utf-8 -*-

# Copyright (c) 2013, Sergio Callegari
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

import numpy as np
import cvxpy


def ntf_fir_from_digested(Qs, A, C, H_inf, **opts):
    """
    Synthesize FIR NTF from predigested specification

    Version for the cvxpy modeler.
    """
    verbose = opts['show_progress']
    if opts['cvxpy_opts']['solver'] == 'cvxopt':
        opts['cvxpy_opts']['solver'] = cvxpy.CVXOPT
    elif opts['cvxpy_opts']['solver'] == 'scs':
        opts['cvxpy_opts']['solver'] = cvxpy.SCS
    order = np.size(Qs, 0)-1
    br = cvxpy.Variable(order, 1, name='br')
    b = cvxpy.vstack(1, br)
    X = cvxpy.Semidef(order, name='X')
    target = cvxpy.Minimize(cvxpy.norm2(Qs*b))
    B = np.vstack((np.zeros((order-1, 1)), 1.))
    C = C+br[::-1].T
    D = np.matrix(1.)
    M1 = A.T*X
    M2 = M1*B
    M = cvxpy.vstack(
        cvxpy.hstack(M1*A-X, M2, C.T),
        cvxpy.hstack(M2.T, B.T*X*B-H_inf**2, D),
        cvxpy.hstack(C, D, np.matrix(-1.))
        )
    Mconstr = -cvxpy.Semidef(order+2)
    constraints = [
        cvxpy.diag(Mconstr) == cvxpy.diag(M),
        cvxpy.upper_tri(Mconstr) == cvxpy.upper_tri(M),
    ]
    p = cvxpy.Problem(target, constraints)
    p.solve(verbose=verbose, **opts['cvxpy_opts'])
    return np.hstack((1, np.asarray(br.value.T)[0]))
