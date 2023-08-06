# -*- coding: utf-8 -*-
# Copyright 2007-2011 The Hyperspy developers
#
# This file is part of  Hyperspy.
#
#  Hyperspy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
#  Hyperspy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with  Hyperspy.  If not, see <http://www.gnu.org/licenses/>.

import scipy as sp
import numpy as np
from numpy import complex128 as complex_
from scipy import constants

from hyperspy.component import Component


class EELS_plane(Component):

    """
    """

    def __init__(
            self, b=4e-8, x0=0, width=1.0, area=1.0, v=2.33e8):
        Component.__init__(self, ('b', 'x0', 'width', 'area', 'v'))

        self.b.value = b
        self.b.ext_force_positive = True

        self.x0.value = x0
        self.width.value = width
        self.width.free = False

        self.area.value = area
        self.area.ext_force_positive = True

        self.v.value = v
        self.v.free = False

        self.v.units = 'm/s'
        self.b.units = 'm'

        self.epsilon = None
        self._eps_file = ''
        self.eps_type_n = True
        self.eps_set = False

        self._eps_en = None
        self._eps_re = None
        self._eps_im = None

        self.phi_out = 1e-6

    @property
    def eps_file(self):
        return self._eps_file

    @eps_file.setter
    def eps_file(self, value):
        if value != '':
            self._eps_file = value
            import copy
            if self.eps_type_n:
# assume epsilon <==> eV and n <==> lambda in files
                tab = np.loadtxt(value, skiprows=3)
                cxheV = constants.physical_constants[
                    'Planck constant in eV s'][0] * constants.c
                self._eps_en = cxheV / copy.deepcopy(tab[:, 0] * 1e-6)
                self._eps_re = copy.deepcopy(tab[:, 1] ** 2 - tab[:, 2] ** 2)
                self._eps_im = copy.deepcopy(tab[:, 1] * tab[:, 2] * 2.0)
            else:
                tab = np.loadtxt(value)
                self._eps_en = copy.deepcopy(tab[:, 0])
                self._eps_re = copy.deepcopy(tab[:, 1])
                self._eps_im = copy.deepcopy(tab[:, 2])

            def epsf(x):
                re = np.interp(
                    x, self._eps_en, self._eps_re, left=self._eps_re[
                        np.argmin(
                            self._eps_en)], right=self._eps_re[
                        np.argmax(
                            self._eps_en)])
                im = np.interp(
                    x, self._eps_en, self._eps_im, left=self._eps_im[
                        np.argmin(
                            self._eps_en)], right=self._eps_im[
                        np.argmax(
                            self._eps_en)])
                return complex_(re + 1j * im)
            self.epsilon = epsf

    def function(self, x):
        """
        This functions it too complicated to explain
        """
        if self.epsilon is None:
            return np.nan

        b = self.b.value
        x0 = self.x0.value
        width = self.width.value
        area = self.area.value
        v = self.v.value
        ax = (x - x0) * width
        # assume axis (and x, ax, etc) is in eV:
        cxheV = constants.physical_constants[
            'Planck constant in eV s'][0] * constants.c
        wavelength = cxheV / ax
        k = 2 * np.pi / wavelength
        omega = k * constants.c
        eps1 = complex_(1.0)
        eps2 = self.epsilon(ax)
        #res = np.empty(ax.shape)
        #for num, r in res:
        try:
            len(ax)
            res = np.empty(ax.shape)
            for num, r in enumerate(res):
                def integrand(q_y):
                    q_parall = np.sqrt((omega[num]/v)**2 + q_y**2)
                    q_z1 = np.sqrt(eps1*k[num]**2 - q_parall**2)
                    q_z2 = np.sqrt(eps2[num]*k[num]**2 - q_parall**2)
                    r_p = (eps2[num]*q_z1 - eps1*q_z2) / (eps2[num]*q_z1 + eps1*q_z2)
                    r_s = (q_z1 - q_z2) / (q_z1 + q_z2)
                    a = (q_y * v / (q_z1* constants.c))**2 * r_s - r_p/eps1
                    a *= q_z1 * np.exp(2*1j*q_z1*b)
                    ans = np.real(a) / (q_parall*q_parall)
                    return ans
                r = sp.integrate.quad(integrand, 0, np.inf)[0]
        except TypeError:
            def integrand(q_y):
                q_parall = np.sqrt((omega/v)**2 + q_y**2)
                q_z1 = np.sqrt(eps1*k**2 - q_parall**2)
                q_z2 = np.sqrt(eps2*k**2 - q_parall**2)
                r_p = (eps2*q_z1 - eps1*q_z2) / (eps2*q_z1 + eps1*q_z2)
                r_s = (q_z1 - q_z2) / (q_z1 + q_z2)
                a = (q_y * v / (q_z1* constants.c))**2 * r_s - r_p/eps1
                a *= q_z1 * np.exp(2*1j*q_z1*b)
                ans = np.real(a) / (q_parall*q_parall)
                return ans
            res = sp.integrate.quad(integrand, 0, np.inf)[0]
        res = np.array(res)
        q_c = np.sqrt((constants.m_e* v * self.phi_out)**2 + (constants.hbar* omega/v)**2) /constants.hbar
        bulk = np.log((q_c*q_c - k*k*eps1)/((omega/v)**2 - k*k*eps1))
        bulk *= (v*v/(constants.c**2) - 1/eps1)
        bulk = np.imag(bulk)
        res += bulk
        res *= 2. * constants.e**2 / (np.pi * v*v * constants.hbar)

# TODO: multiplication factor before integral, add bulk part too
        return res
