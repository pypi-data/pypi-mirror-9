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

:mod:`naviframe` Module
#######################

.. image:: /images/naviframe-preview.png


Widget description
==================

Naviframe stands for navigation frame. It's a views manager
for applications.

A naviframe holds views (or pages) as its items. Those items are
organized in a stack, so that new items get pushed on top of the
old, and only the topmost view is displayed at one time. The
transition between views is animated, depending on the theme
applied to the widget.

Naviframe views hold spaces to various elements, which are:

- back button, used to navigate to previous views,
- next button, used to navigate to next views in the stack,
- title label,
- sub-title label,
- title icon and
- content area.


Layout content parts
====================

- ``default`` - The main content of the current page
- ``icon`` - An icon in the title area of the current page
- ``prev_btn`` - A button of the current page to go to the previous page
- ``next_btn`` - A button of the current page to go to the next page


Layout text parts
=================

- ``default`` - Title label in the title area of the current page
- ``subtitle`` - Sub-title label in the title area of the current page

Most of those content objects can be passed at the time of an item
creation (see :py:meth:`~NaviframeItem.push_to`).


Available styles
================

Naviframe items can have different styles, which affect the
transition between views, for example. On the default theme, two of
them are supported:

- ``basic``   - views are switched sliding horizontally, one after the other
- ``overlap`` - like the previous one, but the previous view stays at its place
  and is overlapped by the new


Emitted signals
===============

- ``transition,finished`` - When the transition is finished in changing the item
- ``title,transition,finished`` -  When the title area's transition is finished
- ``title,clicked`` - User clicked title area
- ``focused`` - When the naviframe has received focus. (since 1.8)
- ``unfocused`` - When the naviframe has lost focus. (since 1.8)

All the parts, for content and text, described here will also be
reachable by naviframe **items** direct calls:

- :py:meth:`~efl.elementary.object_item.ObjectItem.delete`
- :py:meth:`~efl.elementary.object_item.ObjectItem.part_text_set`
- :py:meth:`~efl.elementary.object_item.ObjectItem.part_text_get`
- :py:meth:`~efl.elementary.object_item.ObjectItem.part_content_set`
- :py:meth:`~efl.elementary.object_item.ObjectItem.part_content_get`
- :py:meth:`~efl.elementary.object_item.ObjectItem.part_content_unset`
- :py:meth:`~efl.elementary.object_item.ObjectItem.signal_emit`

What happens is that the topmost item of a naviframe will be the
widget's target layout, when accessed directly. Items lying below
the top one can be interacted with this way.


Inheritance diagram
===================

.. inheritance-diagram:: efl.elementary.naviframe
    :parts: 2

"""

from cpython cimport PyUnicode_AsUTF8String

from efl.eo cimport _object_mapping_register, object_from_instance
from efl.utils.conversions cimport _ctouni
from efl.evas cimport Object as evasObject
from layout_class cimport LayoutClass

from object_item cimport _object_item_to_python, _object_item_list_to_python, \
    ObjectItem

from efl.utils.deprecated cimport DEPRECATED

cdef class NaviframeItem(ObjectItem):
    """

    An item for the Naviframe widget.

    """

    cdef:
        object label, item_style
        Evas_Object *prev_btn
        Evas_Object *next_btn
        Evas_Object *item_content

    def __cinit__(self):
        self.prev_btn = NULL
        self.next_btn = NULL
        self.item_content = NULL

    def __init__(self, title_label = None, evasObject prev_btn = None,
        evasObject next_btn = None, evasObject content = None,
        item_style = None, *args, **kwargs):

        """The following styles are available for this item:

        - ``"default"``

        :param title_label: The label in the title area. The name of the
            title label part is "elm.text.title"
        :type title_label: string
        :param prev_btn: The button to go to the previous item. If it is
            None, then naviframe will create a back button automatically. The
            name of the prev_btn part is "elm.swallow.prev_btn"
        :type prev_btn: :py:class:`~efl.elementary.button.Button`
        :param next_btn: The button to go to the next item. Or It could be
            just an extra function button. The name of the next_btn part is
            "elm.swallow.next_btn"
        :type next_btn: :py:class:`~efl.elementary.button.Button`
        :param content: The main content object. The name of content part is
            "elm.swallow.content"
        :type content: :py:class:`~efl.elementary.object.Object`
        :param item_style: The current item style name. ``None`` would be
            default.
        :type item_style: string

        """
        if isinstance(title_label, unicode): title_label = PyUnicode_AsUTF8String(title_label)
        self.label = title_label

        if prev_btn is not None:
            self.prev_btn = prev_btn.obj
        if next_btn is not None:
            self.next_btn = next_btn.obj
        if content is not None:
            self.item_content = content.obj

        self.args = args
        self.kwargs = kwargs

    def push_to(self, Naviframe naviframe):
        """Push a new item to the top of the naviframe stack (and show it).

        The item pushed becomes one page of the naviframe, this item will be
        deleted when it is popped.

        .. seealso::
            :py:attr:`style`
            :py:func:`insert_before()`
            :py:func:`insert_after()`

        :return: The created item or ``None`` upon failure.
        :rtype: :py:class:`NaviframeItem`

        """
        cdef Elm_Object_Item *item = elm_naviframe_item_push(
            naviframe.obj,
            <const char *>self.label if self.label is not None else NULL,
            self.prev_btn,
            self.next_btn,
            self.item_content,
            <const char *>self.item_style if self.item_style is not None else NULL)

        if item == NULL:
            raise RuntimeError("The item could not be added to the widget.")

        self._set_obj(item)
        self._set_properties_from_keyword_args(self.kwargs)
        return self

    def insert_before(self, NaviframeItem before):
        """Insert a new item into the naviframe before item *before*.

        The item is inserted into the naviframe straight away without any
        transition operations. This item will be deleted when it is popped.

        .. seealso::
            :py:attr:`style`
            :py:func:`push_to()`
            :py:func:`insert_after()`

        :param before: The naviframe item to insert before.
        :type before: :py:class:`NaviframeItem`

        :return: The created item or ``None`` upon failure.
        :rtype: :py:class:`NaviframeItem`

        """
        cdef Naviframe naviframe = before.widget
        cdef Elm_Object_Item *item

        item = elm_naviframe_item_insert_before(
            naviframe.obj,
            before.item,
            <const char *>self.label if self.label is not None else NULL,
            self.prev_btn,
            self.next_btn,
            self.item_content,
            <const char *>self.item_style if self.item_style is not None else NULL)

        if item == NULL:
            raise RuntimeError("The item could not be added to the widget.")

        self._set_obj(item)
        self._set_properties_from_keyword_args(self.kwargs)
        return self

    def insert_after(self, NaviframeItem after):
        """Insert a new item into the naviframe after item *after*.

        The item is inserted into the naviframe straight away without any
        transition operations. This item will be deleted when it is popped.

        .. seealso::
            :py:attr:`style`
            :py:func:`push_to()`
            :py:func:`insert_before()`

        :param after: The naviframe item to insert after.
        :type after: :py:class:`NaviframeItem`

        :return: The created item or ``None`` upon failure.
        :rtype: :py:class:`NaviframeItem`

        """
        cdef Naviframe naviframe = after.widget
        cdef Elm_Object_Item *item

        item = elm_naviframe_item_insert_after(
            naviframe.obj,
            after.item,
            <const char *>self.label if self.label is not None else NULL,
            self.prev_btn,
            self.next_btn,
            self.item_content,
            <const char *>self.item_style if self.item_style is not None else NULL)

        if item == NULL:
            raise RuntimeError("The item could not be added to the widget.")

        self._set_obj(item)
        self._set_properties_from_keyword_args(self.kwargs)
        return self

    @DEPRECATED("1.8", "Use :py:func:`pop_to` instead.")
    def item_pop_to(self):
        elm_naviframe_item_pop_to(self.item)

    def pop_to(self):
        """Pop the items between the top and the above one on the given item."""
        elm_naviframe_item_pop_to(self.item)

    @DEPRECATED("1.8", "Use :py:func:`promote` instead.")
    def item_promote(self):
        elm_naviframe_item_promote(self.item)

    def promote(self):
        """Promote an item already in the naviframe stack to the top of the
        stack

        This will take the indicated item and promote it to the top of the
        stack as if it had been pushed there. The item must already be
        inside the naviframe stack to work.

        """
        elm_naviframe_item_promote(self.item)

    property style:
        """The item style.

        The following styles are available for this item:

        - ``"default"``

        :type: string

        """
        def __get__(self):
            return _ctouni(elm_naviframe_item_style_get(self.item))

        def __set__(self, style):
            if isinstance(style, unicode): style = PyUnicode_AsUTF8String(style)
            elm_naviframe_item_style_set(self.item,
                <const char *>style if style is not None else NULL)

    def style_set(self, style):
        if isinstance(style, unicode): style = PyUnicode_AsUTF8String(style)
        elm_naviframe_item_style_set(self.item,
            <const char *>style if style is not None else NULL)
    def style_get(self):
        return _ctouni(elm_naviframe_item_style_get(self.item))

    property title_visible:
        """Show/Hide the title area

        When the title area is invisible, then the controls would be hidden
        so as to expand the content area to full-size.

        :type: bool

        .. deprecated:: 1.9
            Use :py:attr:`title_enabled` instead.

        """
        def __get__(self):
            return bool(elm_naviframe_item_title_visible_get(self.item))

        def __set__(self, visible):
            elm_naviframe_item_title_visible_set(self.item, visible)

    @DEPRECATED("1.9", "Use :py:func:`title_enabled_set` instead.")
    def title_visible_set(self, visible):
        elm_naviframe_item_title_visible_set(self.item, visible)
    @DEPRECATED("1.9", "Use :py:func:`title_enabled_get` instead.")
    def title_visible_get(self):
        return bool(elm_naviframe_item_title_visible_get(self.item))

    property title_enabled:
        """Enable/Disable the title area and the transition effect.

        When the title area is disabled, then the controls would be hidden so as
        to expand the content area to full-size.

        :type: getter: bool - setter: (bool, bool)

        .. note:: This property is somehow strange, the setter and the getter
                  have different param numbers. The second param in the setter
                  choose if the title transition should be animated or not

        .. seealso:: :py:func:`title_enabled_set` and :py:func:`title_enabled_set`

        .. versionadded:: 1.9

        """
        def __get__(self):
            return bool(elm_naviframe_item_title_enabled_get(self.item))

        def __set__(self, value):
            enabled, transition = value
            elm_naviframe_item_title_enabled_set(self.item, enabled, transition)

    def title_enabled_set(self, enabled, transition):
        """title_enabled_set(self, enabled, transition)

        Enable/Disable the title area with transition effect.

        :param enabled: if `True`, title area will be visible, hidden otherwise.
        :type enabled: bool
        :param transition: if `True`, transition effect of the title will be visible.
        :type transition: bool

        .. versionadded:: 1.9

        """
        elm_naviframe_item_title_enabled_set(self.item, enabled, transition)

    def title_enabled_get(self):
        """

        :return: `True` if the title is visible.
        :rtype: bool

        .. versionadded:: 1.9

        """
        return bool(elm_naviframe_item_title_enabled_get(self.item))


cdef class Naviframe(LayoutClass):
    """

    This is the class that actually implements the widget.

    """

    def __init__(self, evasObject parent, *args, **kwargs):
        """Naviframe(...)

        :param parent: The parent object
        :type parent: :py:class:`efl.evas.Object`
        :param \**kwargs: All the remaining keyword arguments are interpreted
                          as properties of the instance

        """
        self._set_obj(elm_naviframe_add(parent.obj))
        self._set_properties_from_keyword_args(kwargs)

    def item_push(self, title_label, evasObject prev_btn, evasObject next_btn, evasObject content, item_style):
        return NaviframeItem(title_label, prev_btn, next_btn, content, item_style).push_to(self)

    def item_insert_before(self, NaviframeItem before, title_label, evasObject prev_btn, evasObject next_btn, evasObject content, item_style):
        return NaviframeItem(title_label, prev_btn, next_btn, content, item_style).insert_before(before)

    def item_insert_after(self, NaviframeItem after, title_label, evasObject prev_btn, evasObject next_btn, evasObject content, item_style):
        return NaviframeItem(title_label, prev_btn, next_btn, content, item_style).insert_after(after)

    def item_pop(self):
        """Pop an item that is on top of the stack

        This pops an item that is on the top (visible) of the naviframe,
        makes it disappear, then deletes the item. The item that was
        underneath it on the stack will become visible.

        .. seealso:: :py:attr:`content_preserve_on_pop`

        :return: ``None`` or the content object(if
            :py:attr:`content_preserve_on_pop` is True).
        :rtype: :py:class:`~efl.evas.Object`

        """
        return object_from_instance(elm_naviframe_item_pop(self.obj))

    property content_preserve_on_pop:
        """Preserve the content objects when items are popped.

        :type: bool

        """
        def __get__(self):
            return bool(elm_naviframe_content_preserve_on_pop_get(self.obj))
        def __set__(self, preserve):
            elm_naviframe_content_preserve_on_pop_set(self.obj, preserve)

    def content_preserve_on_pop_set(self, preserve):
        elm_naviframe_content_preserve_on_pop_set(self.obj, preserve)
    def content_preserve_on_pop_get(self):
        return bool(elm_naviframe_content_preserve_on_pop_get(self.obj))

    property top_item:
        """Get a top item on the naviframe stack

        :type: :py:class:`NaviframeItem`

        """
        def __get__(self):
            return _object_item_to_python(elm_naviframe_top_item_get(self.obj))

    def top_item_get(self):
        return _object_item_to_python(elm_naviframe_top_item_get(self.obj))

    property bottom_item:
        """Get a bottom item on the naviframe stack

        :type: :py:class:`NaviframeItem`

        """
        def __get__(self):
            return _object_item_to_python(elm_naviframe_bottom_item_get(self.obj))

    def bottom_item_get(self):
        return _object_item_to_python(elm_naviframe_bottom_item_get(self.obj))

    property prev_btn_auto_pushed:
        """Whether prev button(back button) will be created automatically or
        not.

        .. seealso:: item_push()

        :type: bool

        """
        def __get__(self):
            return bool(elm_naviframe_prev_btn_auto_pushed_get(self.obj))
        def __set__(self, auto_pushed):
            elm_naviframe_prev_btn_auto_pushed_set(self.obj, auto_pushed)

    def prev_btn_auto_pushed_set(self, auto_pushed):
        elm_naviframe_prev_btn_auto_pushed_set(self.obj, auto_pushed)
    def prev_btn_auto_pushed_get(self):
        return bool(elm_naviframe_prev_btn_auto_pushed_get(self.obj))

    property items:
        """Get a list of all the naviframe items.

        :type: tuple of :py:class:`NaviframeItem`

        """
        def __get__(self):
            return _object_item_list_to_python(elm_naviframe_items_get(self.obj))

    def items_get(self):
        return _object_item_list_to_python(elm_naviframe_items_get(self.obj))

    property event_enabled:
        """Whether the event when pushing/popping items is enabled

        If is True, the contents of the naviframe item will receives events
        from mouse and keyboard during view changing such as item push/pop.

        .. warning::
            Events will be blocked by setting
            :py:attr:`~efl.evas.Object.freeze_events` internally.
            So don't call the API while pushing/popping items.

        :type: bool

        """
        def __get__(self):
            return bool(elm_naviframe_event_enabled_get(self.obj))
        def __set__(self, enabled):
            elm_naviframe_event_enabled_set(self.obj, enabled)

    def event_enabled_set(self, enabled):
        elm_naviframe_event_enabled_set(self.obj, enabled)
    def event_enabled_get(self):
        return bool(elm_naviframe_event_enabled_get(self.obj))

    def item_simple_push(self, evasObject content):
        """Simple version of :py:func:`NaviframeItem.push_to()`.

        .. seealso:: :py:func:`NaviframeItem.push_to()`

        """
        cdef NaviframeItem ret = NaviframeItem()
        cdef Elm_Object_Item *item

        item = elm_naviframe_item_simple_push(self.obj, content.obj)
        if item != NULL:
            ret._set_obj(item)
            return ret
        else:
            return None

    def item_simple_promote(self, evasObject content):
        """Simple version of :py:func:`NaviframeItem.promote()`.

        .. seealso:: :py:func:`NaviframeItem.promote()`

        """
        elm_naviframe_item_simple_promote(self.obj, content.obj)

    def callback_transition_finished_add(self, func, *args, **kwargs):
        """When the transition is finished in changing the item."""
        self._callback_add("transition,finished", func, *args, **kwargs)

    def callback_transition_finished_del(self, func):
        self._callback_del("transition,finished", func)

    def callback_title_transition_finished_add(self, func, *args, **kwargs):
        """When the title transition is finished."""
        self._callback_add("title,transition,finished", func, *args, **kwargs)

    def callback_title_transition_finished_del(self, func):
        self._callback_del("title,transition,finished", func)

    def callback_title_clicked_add(self, func, *args, **kwargs):
        """User clicked title area."""
        self._callback_add("title,clicked", func, *args, **kwargs)

    def callback_title_clicked_del(self, func):
        self._callback_del("title,clicked", func)

    def callback_focused_add(self, func, *args, **kwargs):
        """When the naviframe has received focus.

        .. versionadded:: 1.8
        """
        self._callback_add("focused", func, *args, **kwargs)

    def callback_focused_del(self, func):
        self._callback_del("focused", func)

    def callback_unfocused_add(self, func, *args, **kwargs):
        """When the naviframe has lost focus.

        .. versionadded:: 1.8
        """
        self._callback_add("unfocused", func, *args, **kwargs)

    def callback_unfocused_del(self, func):
        self._callback_del("unfocused", func)

_object_mapping_register("Elm_Naviframe", Naviframe)
