#!/usr/bin/env python

import efl.ecore
from efl.ecore.x import init, Window, on_window_configure_add

init()

# method 1
main_window = Window(w=800, h=600)
main_window.background_color_set(0xffff, 0, 0)
main_window.show()

sub_window = Window(main_window, 10, 10, 780, 580)
sub_window.background_color_set(0, 0, 0xffff)
sub_window.show()


def cb_on_configure(event, main_window, sub_window):
    if event.win == main_window:
        sub_window.resize(event.w - 20, event.h - 20)
    return True
on_window_configure_add(cb_on_configure, main_window, sub_window)


# method 2: inheritance
class MyWindow(Window):
    def __init__(self, w, h):
        Window.__init__(self, w=w, h=h)
        self.background_color_set(0xffff, 0, 0)
        self.sub_window = Window(self, 10, 10, w - 20, h - 20)
        self.sub_window.background_color_set(0, 0, 0xffff)
        self.sub_window.show()
        on_window_configure_add(self._cb_on_configure)

    def _cb_on_configure(self, event):
        if event.win == self:
            self.sub_window.resize(event.w - 20, event.h - 20)
        return True

other_window = MyWindow(400, 300)
other_window.show()

efl.ecore.main_loop_begin()
