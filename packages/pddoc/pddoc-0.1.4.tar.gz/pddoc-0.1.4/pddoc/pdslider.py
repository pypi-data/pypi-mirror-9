#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2015 by Serge Poltavski                                 #
#   serge.poltavski@gmail.com                                             #
#                                                                         #
#   This program is free software; you can redistribute it and/or modify  #
#   it under the terms of the GNU General Public License as published by  #
#   the Free Software Foundation; either version 3 of the License, or     #
#   (at your option) any later version.                                   #
#                                                                         #
#   This program is distributed in the hope that it will be useful,       #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#   GNU General Public License for more details.                          #
#                                                                         #
#   You should have received a copy of the GNU General Public License     #
#   along with this program. If not, see <http://www.gnu.org/licenses/>   #

 
__author__ = 'Serge Poltavski'


from pdcoregui import *


class PdSlider(PdCoreGui):
    def __init__(self, name, x, y, **kwargs):
        PdCoreGui.__init__(self, name, x, y, [], **kwargs)
        self._min = float(kwargs.get("min", 0))
        self._max = float(kwargs.get("max", 127))
        assert self._min <= self._max
        self._log = int(kwargs.get("log", 0))
        self._init = int(kwargs.get("init", 0))
        self._default_value = int(kwargs.get("default_value", 0))
        self._steady = int(kwargs.get("steady", 0))
        self._value = float(kwargs.get("value", self._min))
        self._pad = 3

    def slider_width(self):
        if self._value == self._max / 2:
            return 5
        else:
            return 3

    @staticmethod
    def from_atoms(atoms):
        assert isinstance(atoms, list) and len(atoms) == 19
        assert atoms[0] in ("hsl", "vsl")

        if atoms[0] == "hsl":
            return PdHSlider(0, 0,
                             width=atoms[1],
                             height=atoms[2],
                             min=atoms[3],
                             max=atoms[4],
                             log=atoms[5],
                             init=atoms[6],
                             send=atoms[7],
                             receive=atoms[8],
                             label=atoms[9],
                             label_xoff=atoms[10],
                             label_yoff=atoms[11],
                             font_type=atoms[12],
                             font_size=atoms[13],
                             bg_color=atoms[14],
                             fg_color=atoms[15],
                             label_color=atoms[16],
                             default_value=atoms[17],
                             steady=atoms[18])
        else:
            return PdVSlider(0, 0,
                             width=atoms[1],
                             height=atoms[2],
                             min=atoms[3],
                             max=atoms[4],
                             log=atoms[5],
                             init=atoms[6],
                             send=atoms[7],
                             receive=atoms[8],
                             label=atoms[9],
                             label_xoff=atoms[10],
                             label_yoff=atoms[11],
                             font_type=atoms[12],
                             font_size=atoms[13],
                             bg_color=atoms[14],
                             fg_color=atoms[15],
                             label_color=atoms[16],
                             default_value=atoms[17],
                             steady=atoms[18])


class PdHSlider(PdSlider):
    def __init__(self, x, y, **kwargs):
        PdSlider.__init__(self, "hsl", x, y, **kwargs)
        self.width = int(kwargs.get("width", 128))
        self.height = int(kwargs.get("height", 15))

    def draw(self, painter):
        self.draw_bbox(painter)
        self.draw_label(painter)

        xoff = self._value / self._max
        x = int(self.left + self._pad + (self.width - self._pad) * xoff)
        painter.draw_line(x, self.top, x, self.bottom, color=self.fgcolor(), width=self.slider_width())

        self.draw_xlets(painter)


class PdVSlider(PdSlider):
    def __init__(self, x, y, **kwargs):
        PdSlider.__init__(self, "vsl", x, y, **kwargs)

        self.width = int(kwargs.get("width", 15))
        self.height = int(kwargs.get("height", 128))

    def draw(self, painter):
        self.draw_bbox(painter)
        self.draw_label(painter)

        assert self._value < self._max

        yoff = self._value / self._max
        y = int(self.bottom - self._pad - (self.height - self._pad) * yoff)
        painter.draw_line(self.left, y, self.right, y, color=self.fgcolor(), width=self.slider_width())

        self.draw_xlets(painter)
