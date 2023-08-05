#!/usr/bin/env python
#coding=UTF-8

from efl.evas import Canvas, Textgrid, TextgridCell
import unittest


class TestTextgridBasics(unittest.TestCase):
    def setUp(self):
        self.canvas = Canvas(
            method="buffer",
            size=(400, 500),
            viewport=(0, 0, 400, 500)
        )
        self.canvas.engine_info_set(self.canvas.engine_info_get())

    def tearDown(self):
        self.canvas.delete()
        del self.canvas

    def testTextgridConstructor(self):
        tg = Textgrid(self.canvas)
        self.assertEqual(type(tg), Textgrid)

    def testTextgrid(self):
        tg = Textgrid(self.canvas)
        tg.size = 10, 10
        row = tg.cellrow_get(0)
        for cell in row:
            cell.codepoint = "ö"
            cell.bold = True
        tg.cellrow_set(0, row)
        tg.update_add(0, 0, 10, 1)
        rowback = tg.cellrow_get(0)
        print(tg.cell_size)
        self.assertEqual(row[0].codepoint, rowback[0].codepoint)


if __name__ == '__main__':
    unittest.main(verbosity=2)
    evas.shutdown()
