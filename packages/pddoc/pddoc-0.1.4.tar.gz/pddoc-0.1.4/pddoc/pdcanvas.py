#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2014 by Serge Poltavski                                 #
# serge.poltavski@gmail.com                                             #
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

from pdobject import *
from pdcomment import PdComment
import common


class PdCanvas(PdObject):
    TYPE_NONE, TYPE_WINDOW, TYPE_SUBPATCH, TYPE_GRAPH = range(0, 4)

    def __init__(self, x, y, w, h, **kwargs):
        PdObject.__init__(self, "cnv", x, y, w, h)
        self._objects = []
        self._id_counter = 0
        self._name = ""
        self._type = self.TYPE_NONE
        self._graphs = []
        self._connections = {}

        if 'name' in kwargs:
            self._name = kwargs['name']

        if 'open_on_load' in kwargs:
            self.open_on_load = kwargs['open_on_load']

    @property
    def objects(self):
        return self._objects

    @property
    def graphs(self):
        return self._graphs

    @property
    def connections(self):
        return self._connections

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, t):
        assert t in (self.TYPE_NONE, self.TYPE_WINDOW, self.TYPE_SUBPATCH, self.TYPE_GRAPH)
        self._type = t

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def append_graph(self, obj):
        assert self != obj
        assert isinstance(obj, PdCanvas)
        assert obj.type == self.TYPE_GRAPH
        self.append_object(obj)

    def gen_object_id(self):
        res = self._id_counter
        self._id_counter += 1
        return res

    def append_object(self, obj):
        assert self != obj
        assert issubclass(obj.__class__, PdBaseObject)

        if obj in self._objects:
            common.warning(u"object already on canvas: {0:s}".format(obj))
            return False

        obj.id = self.gen_object_id()
        self.objects.append(obj)
        return True

    def find_object_by_id(self, oid):
        for obj in self._objects:
            if issubclass(obj.__class__, PdObject):
                if obj.id == oid:
                    return obj

        return None

    @staticmethod
    def make_connection_key(sid, soutl, did, dinl):
        return "%i:%i => %i:%i" % (sid, soutl, did, dinl)

    def add_connection(self, sid, soutl, did, dinl, check_xlets=True):
        assert sid != did
        assert sid >= 0 and did >= 0 and soutl >= 0 and dinl >= 0

        def str_bbox(obj, xlet):
                if obj:
                    return "[%s:%d]" % (obj.name, xlet)
                else:
                    return "[?:%d]" % xlet

        src_obj = self.find_object_by_id(sid)
        dest_obj = self.find_object_by_id(did)

        if src_obj and dest_obj:

            if check_xlets:
                if soutl >= len(src_obj.outlets()):
                    common.warning(u"[{0:s}] invalid outlet number: {1:d}, total outlets: {2:d}".
                                   format(src_obj.name, soutl, len(src_obj.outlets())))
                    return False

                if dinl >= len(dest_obj.inlets()):
                    common.warning(u"[{0:s}] invalid inlet number: {1:d}, total inlets: {2:d}".
                                   format(dest_obj.name, dinl, len(dest_obj.inlets())))
                    return False

            ckey = PdCanvas.make_connection_key(sid, soutl, did, dinl)
            self._connections[ckey] = (src_obj, soutl, dest_obj, dinl)
            return True
        else:
            common.warning("%s => %s" % (str_bbox(src_obj, soutl), str_bbox(dest_obj, dinl)))
            # common.warning("[%s:%d] => [%s:%d]" % (src_obj.name, soutl, dest_obj.name, dinl))
            common.warning("connection not found: %s:%d => %s:%d in canvas: %s" % (sid, soutl, did, dinl, self.name))
            return False

    def connect(self, args):
        assert len(args) == 4
        src_id = int(args[0])
        src_outl = int(args[1])
        dest_id = int(args[2])
        dest_inl = int(args[3])

        self.add_connection(src_id, src_outl, dest_id, dest_inl)

    def append_subpatch(self, obj):
        assert self != obj
        assert isinstance(obj, PdCanvas)
        assert obj.type == self.TYPE_SUBPATCH
        self.append_object(obj)
        return True

    def __str__(self):
        if self.type == self.TYPE_WINDOW:
            name = "Canvas "
        elif self.type == self.TYPE_GRAPH:
            name = "Graph "
        elif self.type == self.TYPE_SUBPATCH:
            name = "Subpatch "
        else:
            print self.name
            assert False

        name += u"\"{0:s}\"".format(self.name)

        res = "%-30s (%i,%i %ix%i id:%i)\n" % (name, self._x, self._y, self._width, self._height, self.id)
        for obj in self.objects:
            res += "    " + str(obj)
            res += "\n"

        return res

    def draw(self, painter):
        if self.type == self.TYPE_NONE:
            return

        if self.type == self.TYPE_SUBPATCH:
            painter.draw_subpatch(self)
        elif self.type == self.TYPE_GRAPH:
            painter.draw_graph(self)
        elif self.type == self.TYPE_WINDOW:
            painter.draw_canvas(self)

            for obj in self._objects:
                obj.draw(painter)

            painter.draw_connections(self)

    def inlets(self):
        res = []

        objects = sorted(self._objects, key=lambda obj: obj.x)

        for o in objects:
            if issubclass(o.__class__, PdObject):
                if o.name == "inlet":
                    res.append(self.XLET_MESSAGE)
                elif o.name == "inlet~":
                    res.append(self.XLET_SOUND)

        return res

    def outlets(self):
        res = []

        objects = sorted(self._objects, key=lambda obj: obj.x)

        for o in objects:
            if issubclass(o.__class__, PdObject):
                if o.name == "outlet":
                    res.append(self.XLET_MESSAGE)
                elif o.name == "outlet~":
                    res.append(self.XLET_SOUND)

        return res

    def traverse(self, visitor):
        if hasattr(visitor, 'visit_canvas_begin'):
            visitor.visit_canvas_begin(self)

        for o in self.objects:
            o.traverse(visitor)

        for k, conn in self._connections.items():
            visitor.visit_connection(conn)

        if hasattr(visitor, 'visit_canvas_end'):
            visitor.visit_canvas_end(self)

    def _print_connections(self):
        for k, v in self.connections.items():
            print "[%s:%d (%d,%d)] => [%s:%d (%d,%d)]" % (v[0].name, v[1], v[0].x, v[0].y,
                                                          v[2].name, v[3], v[2].x, v[2].y)