#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015 Timothée Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np

#transforms between screen coordinates and plot coordinates
class CoordinateTransform(object):
    def __init__(self, min, max, length, startBorder, endBorder):
        super(CoordinateTransform, self).__init__()

        self.min = min
        self.max = max
        self.length = length
        self.startBorder = startBorder
        self.endBorder = endBorder
        self.log = False

    def setRange(self, min, max):
        self.min = min
        self.max = max

    def setLength(self, length):
        self.length = length

    def setBorders(self, start, end):
        self.startBorder = start
        self.endBorder = end

    def setLinear(self):
        self.log = False

    def setLogarithmic(self):
        self.log = True

    def toScreen(self, x):
        if self.max == self.min:
            return self.startBorder + 0.*x # keep x type (this can produce a RunTimeWarning if x contains inf)

        if self.log:
            logMin = max(1e-20, self.min)
            logMax = max(logMin, self.max)
            x = (x<1e-20)*1e-20 + (x>=1e-20)*x
            return (np.log10(x/logMin))*(self.length - self.startBorder - self.endBorder)/np.log10(logMax/logMin) + self.startBorder
        else:
            return (x - self.min)*(self.length - self.startBorder - self.endBorder)/(self.max - self.min) + self.startBorder

    def toPlot(self, x):
        if self.length == self.startBorder + self.endBorder:
            return self.min + 0.*x # keep x type (this can produce a RunTimeWarning if x contains inf)

        if self.log:
            return 10**((x - self.startBorder)*np.log10(self.max/self.min)/(self.length - self.startBorder - self.endBorder))*self.min
        else:
            return (x - self.startBorder)*(self.max - self.min)/(self.length - self.startBorder - self.endBorder) + self.min
