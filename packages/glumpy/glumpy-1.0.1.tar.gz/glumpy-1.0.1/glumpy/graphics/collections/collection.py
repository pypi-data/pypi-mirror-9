# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
A collection is a container for several items having the same data
structure (dtype). Each data type can be declared as local (it specific to a
vertex), shared (it is shared among an item vertices) or global (it is shared
by all vertices). It is based on the BaseCollection but offers a more intuitive
interface.
"""

import os
import numpy as np
from glumpy import gloo, gl
from glumpy.gloo.program import Program
from glumpy.transforms import Position, Viewport
from . util import fetchcode
from . base_collection import BaseCollection


class Collection(BaseCollection):
    """
    A collection is a container for several items having the same data
    structure (dtype). Each data type can be declared as local (it is specific
    to a vertex), shared (it is shared among item vertices) or global (it is
    shared by all items). It is based on the BaseCollection but offers a more
    intuitive interface.

    Parameters
    ----------

    dtype: list
        Data individual types as (name, dtype, scope, default)

    itype: np.dtype or None
        Indices data type

    mode : GL_ENUM
        GL_POINTS, GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP,
        GL_TRIANGLES, GL_TRIANGLE_STRIP, GL_TRIANGLE_FAN

    vertex: str or tuple of str
       Vertex shader to use to draw this collection

    fragment:  str or tuple of str
       Fragment shader to use to draw this collection

    kwargs: str
        Scope can also be specified using keyword argument,
        where parameter name must be one of the dtype.
    """

    _gtypes = { ('float32', 1) : "float",
                ('float32', 2) : "vec2",
                ('float32', 3) : "vec3",
                ('float32', 4) : "vec4",
                ('int32', 1)   : "int",
                ('int32', 2)   : "ivec2",
                ('int32', 3)   : "ivec3",
                ('int32', 4)   : "ivec4" }

    def __init__(self, dtype, itype, mode, vertex, fragment, geometry=None, **kwargs):
        """
        """

        self._uniforms = {}
        self._attributes = {}
        self._varyings = {}
        self._mode = mode
        vtype = []
        utype = []

        # Build vtype and utype according to parameters
        declarations = {"uniforms"   : "",
                        "attributes" : "",
                        "varyings"   : ""}
        defaults = {}
        for item in dtype:
            name, (basetype,count), scope, default = item
            basetype = np.dtype(basetype).name
            if scope[0] == "!":
                scope = scope[1:]
            else:
                scope = kwargs.get(name, scope)
            defaults[name] = default
            gtype = Collection._gtypes[(basetype,count)]
            if scope == "local":
                vtype.append( (name, basetype, count) )
                declarations["attributes"] += "attribute %s %s;\n" % (gtype, name)
            elif scope == "shared":
                utype.append( (name, basetype, count) )
                declarations["varyings"] += "varying %s %s;\n" % (gtype, name)
            else:
                declarations["uniforms"] += "uniform %s %s;\n" % (gtype, name)
                self._uniforms[name] = None

        vtype = np.dtype(vtype)
        itype = np.dtype(itype) if itype else None
        utype = np.dtype(utype) if utype else None

        BaseCollection.__init__(self, vtype=vtype, utype=utype, itype=itype)
        self._declarations = declarations
        self._defaults = defaults

        # Build program (once base collection is built)
        saved = vertex
        vertex = ""

        if self.utype is not None:
            vertex += fetchcode(self.utype) + vertex
        else:
            vertex += "void fetch_uniforms(void) { }\n" + vertex
        vertex += self._declarations["uniforms"]
        vertex += self._declarations["attributes"]
        vertex += saved

        self._vertex = vertex
        self._fragment = fragment

        program = Program(vertex, fragment, geometry)
        self._programs.append(program)

        # Initialize uniforms
        for name in self._uniforms.keys():
            self._uniforms[name] = self._defaults.get(name)
            program[name] = self._uniforms[name]



    def view(self, transform, viewport=None):
        """ Return a view on the collection using provided transform """

        program = gloo.Program(self._vertex, self._fragment)
        if "transform" in program.hooks:
            program["transform"] = transform
        if "viewport" in program.hooks:
            if viewport is not None:
                program["viewport"] = viewport
            else:
                program["viewport"] = Viewport()
        self._programs.append(program)
        program.bind(self._vertices_buffer)
        for name in self._uniforms.keys():
            program[name] = self._uniforms[name]
        if self._uniforms_list is not None:
            program["uniforms"] = self._uniforms_texture
            program["uniforms_shape"] = self._ushape
        return program



    def __getitem__(self, key):

        program = self._programs[0]
        if key in program.hooks:
            return program[key]

        for (name,gtype) in program.all_uniforms:
            if name == key:
                return program[key]

        return BaseCollection.__getitem__(self, key)


    def __setitem__(self, key, value):

        found = False
        for program in self._programs:
            for (name,gtype) in program.all_uniforms:
                if name == key:
                    found = True
                    program[key] = value
        if not found:
            BaseCollection.__setitem__(self, key, value)


    def draw(self, mode = None):
        """ Draw collection """

        if self._need_update:
            self._update()

        program = self._programs[0]

        mode = mode or self._mode
        if self._indices_list is not None:
            program.draw(mode, self._indices_buffer)
        else:
            program.draw(mode)
