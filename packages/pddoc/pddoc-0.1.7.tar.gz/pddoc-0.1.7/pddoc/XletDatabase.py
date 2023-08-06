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

from pdbaseobject import PdBaseObject


class XletDatabase(object):
    XLET_MESSAGE = PdBaseObject.XLET_MESSAGE
    XLET_SOUND = PdBaseObject.XLET_SOUND

    def __init__(self, extname=None):
        self._extname = extname

    def has_object(self, name):
        return False

    def inlets(self, name, args=[]):
        return []

    def outlets(self, name, args=[]):
        return []

    @property
    def extname(self):
        return self._extname