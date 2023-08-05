# Copyright (C) 2007-2015 various contributors (see AUTHORS)
#
# This file is part of Python-EFL.
#
# Python-EFL is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# Python-EFL is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this Python-EFL.  If not, see <http://www.gnu.org/licenses/>.


"""

:mod:`grid` Module
##################

.. image:: /images/grid-preview.png


Widget description
==================

A grid layout widget.

The grid is a grid layout widget that lays out a series of children as a
fixed "grid" of widgets using a given percentage of the grid width and
height each using the child object.

The Grid uses a "Virtual resolution" that is stretched to fill the grid
widgets size itself. The default is 100 x 100, so that means the
position and sizes of children will effectively be percentages (0 to 100)
of the width or height of the grid widget.


Inheritance diagram
===================

.. inheritance-diagram:: efl.elementary.grid
    :parts: 2

"""

from efl.eo cimport _object_mapping_register
from efl.evas cimport Object as evasObject
from object cimport Object
from efl.utils.conversions cimport eina_list_objects_to_python_list

cdef class Grid(Object):
    """

    This is the class that actually implement the widget.

    """

    def __init__(self, evasObject parent, *args, **kwargs):
        """Grid(...)

        :param parent: The parent object
        :type parent: :py:class:`efl.evas.Object`
        :param \**kwargs: All the remaining keyword arguments are interpreted
                          as properties of the instance

        """
        self._set_obj(elm_grid_add(parent.obj))
        self._set_properties_from_keyword_args(kwargs)

    property size:
        """The virtual size (width and height) of the grid.

        :type: tuple of Evas_Coords (int)

        """
        def __set__(self, value):
            w, h = value
            elm_grid_size_set(self.obj, w, h)

        def __get__(self):
            cdef Evas_Coord w, h
            elm_grid_size_get(self.obj, &w, &h)
            return (w, h)

    def size_set(self, w, h):
        elm_grid_size_set(self.obj, w, h)
    def size_get(self):
        cdef Evas_Coord w, h
        elm_grid_size_get(self.obj, &w, &h)
        return (w, h)

    def pack(self, evasObject subobj, x, y, w, h):
        """Pack child at given position and size

        :param subobj: The child to pack
        :type subobj: :py:class:`~efl.evas.Object`
        :param x: The virtual x coord at which to pack it
        :type x: Evas_Coord (int)
        :param y: The virtual y coord at which to pack it
        :type y: Evas_Coord (int)
        :param w: The virtual width at which to pack it
        :type w: Evas_Coord (int)
        :param h: The virtual height at which to pack it
        :type h: Evas_Coord (int)

        """
        elm_grid_pack(self.obj, subobj.obj, x, y, w, h)

    def unpack(self, evasObject subobj):
        """Unpack a child from a grid object

        :param subobj: The child to unpack
        :type subobj: :py:class:`~efl.evas.Object`

        """
        elm_grid_unpack(self.obj, subobj.obj)

    def clear(self, clear):
        """Faster way to remove all child objects from a grid object.

        :param clear: If True, will also delete the just removed children
        :type clear: bool

        """
        elm_grid_clear(self.obj, clear)

    property children:
        """Get the list of the children for the grid.

        :type: tuple of :py:class:`~efl.evas.Object`

        """
        def __get__(self):
            return eina_list_objects_to_python_list(elm_grid_children_get(self.obj))

    def children_get(self):
        return eina_list_objects_to_python_list(elm_grid_children_get(self.obj))

def grid_pack_set(evasObject subobj, x, y, w, h):
    """Set packing of an existing child at to position and size

    :param subobj: The child to set packing of
    :type subobj: :py:class:`~efl.evas.Object`
    :param x: The virtual x coord at which to pack it
    :type x: Evas_Coord (int)
    :param y: The virtual y coord at which to pack it
    :type y: Evas_Coord (int)
    :param w: The virtual width at which to pack it
    :type w: Evas_Coord (int)
    :param h: The virtual height at which to pack it
    :type h: Evas_Coord (int)

    """
    elm_grid_pack_set(subobj.obj, x, y, w, h)

def grid_pack_get(evasObject subobj):
    """Get packing of a child

    :param subobj: The child to query
    :type subobj: :py:class:`~efl.evas.Object`

    return: The position and size
    rtype: tuple of Evas_Coords (int)

    """
    cdef Evas_Coord x, y, w, h
    elm_grid_pack_get(subobj.obj, &x, &y, &w, &h)
    return (x, y, w, h)


_object_mapping_register("Elm_Grid", Grid)
