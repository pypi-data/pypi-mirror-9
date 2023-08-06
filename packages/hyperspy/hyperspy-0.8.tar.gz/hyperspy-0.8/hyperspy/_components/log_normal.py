# -*- coding: utf-8 -*-
# Copyright 2007-2011 The HyperSpy developers
#
# This file is part of  HyperSpy.
#
#  HyperSpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
#  HyperSpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with  HyperSpy.  If not, see <http://www.gnu.org/licenses/>.

import math

import numpy as np

from hyperspy.component import Component

sqrt2pi = math.sqrt(2 * math.pi)


class Log_normal(Component):

    """Normalized log-normal function component

    .. math::

        f(x) = \\frac{a}{\sqrt{2\pi x c^{2}}}e^{-\\frac{\left(ln(x)-b\\right)^{2}}{2c^{2}}}

    +------------+-----------+
    | Parameter  | Attribute |
    +------------+-----------+
    +------------+-----------+
    |     a      |     A     |
    +------------+-----------+
    |     b      |  centre   |
    +------------+-----------+
    |     c      |   sigma   |
    +------------+-----------+

    For convenience the `fwhm` attribute can be used to get and set
    the full-with-half-maximum.

    """

    def __init__(self, A=1., sigma=1., centre=0.):
        Component.__init__(self, ['A', 'sigma', 'centre'])
        self.A.value = A
        self.sigma.value = sigma
        self.centre.value = centre
        self._position = self.centre

        # Boundaries

        self.centre.bmin = 0
        self.centre.ext_force_positive = True
        self.centre.free = False

        self.A.bmin = 0.
        self.A.bmax = None

        self.sigma.bmin = None
        self.sigma.bmax = None

        self.isbackground = False
        # self.convolved = True

        # Gradients
        self.A.grad = self.grad_A
        self.sigma.grad = self.grad_sigma
        self.centre.grad = self.grad_centre

    def function(self, x):
        A = self.A.value
        sigma = self.sigma.value
        centre = self.centre.value
        return A * (1 / (x * sigma * sqrt2pi)) * np.exp(
            -(np.log(x) - centre) ** 2 / (2 * sigma ** 2))

    def grad_A(self, x):
        return self.function(x) / self.A.value

    def grad_sigma(self, x):
        s = self.sigma.value
        m = self.centre.value
        fn = self.function(x)
        return (np.log(x) - m)**2 * fn/(s**3) - fn/s

    def grad_centre(self, x):
        s = self.sigma.value
        m = self.centre.value
        fn = self.function(x)
        return (np.log(x) - m) * fn / (s * s)

    @property
    def mean(self):
        return np.exp(self.centre.value + 0.5*self.sigma.value**2)

    @mean.setter
    def mean(self, value):
        variance = value**2 * (np.exp(self.sigma.value**2) -1)
        self.centre.value = np.abs(np.log((value**2) / np.sqrt(variance + value**2)))
