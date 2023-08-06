# Copyright (c) 2015 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division)

from .constants import WHITESPACE

def pairwise(iterable):
    it = iter(iterable)
    a = next(it)

    for b in it:
        yield (a, b)
        a = b


def inc_tuple(tup):
    return (tup[0], tup[1] + 1)


def dec_tuple(tup):
    return (tup[0], tup[1] - 1)


class LineCol(object):

    def __init__(self, code, line, col):
        self.code = code
        self.line, self.col = line, col
        self.adjust()

    def char(self):
        try:
            return self.code[self.line - 1][self.col]
        except IndexError as e:
            raise IndexError(str(e) +
                (": self.code[self.line - 1][self.col] with \n"
                 "self.line = {}; self.col = {}; len(self.code) = {}")
                .format(self.line, self.col, len(self.code)))

    def inc(self):
        self.col += 1
        while len(self.code[self.line - 1]) == self.col and not self.eof:
            self.col = 0
            self.line += 1

    def dec(self):
        self.col -= 1
        while self.col == -1 and not self.bof:
            self.col = len(self.code[self.line - 2]) - 1
            self.line -= 1

    def adjust(self):
        while len(self.code[self.line - 1]) == self.col and not self.eof:
            self.col = 0
            self.line += 1
        while self.col == -1 and not self.bof:
            self.col = len(self.code[self.line - 2]) - 1
            self.line -= 1
    @property
    def eof(self):
        return self.line >= len(self.code) and self.col >= len(self.code[-1])

    @property
    def bof(self):
        return self.line <= 0 and self.col <= 0

    def tuple(self):
        return (self.line, self.col)

    def __lt__(self, other):
        return self.tuple() < other.tuple()

    def __eq__(self, other):
        return self.tuple() == other.tuple()

    def __repr__(self):
        return str(self.tuple())


def find_in_between(position, elements):
    try:
        p1, p2 = elements.find_previous(position)
    except IndexError:
        return None, None
    if not p1 < position < p2:
        return None, None
    return p1, p2


def position_between(code, position1, position2):
    if position1 > position2:
        position1, position2 = position2, position1
    p1, p2 = LineCol(code, *position1), LineCol(code, *position2)

    start = LineCol(code, *position1)
    while start < p2 and start.char() in WHITESPACE:
        start.inc()
    end = LineCol(code, *dec_tuple(position2))
    while end > p1 and end.char() in WHITESPACE:
        end.dec()
    if end > p1:
        end.inc()
    if end == start:
        return position1, position2
    if start > end:
        tup = start.tuple()
        return tup, tup
    return start.tuple(), end.tuple()


def find_next_parenthesis(code, position, parenthesis):
    p1, p2 = find_in_between(position, parenthesis)
    if not p1:
        return

    p2 = LineCol(code, *dec_tuple(p2))
    end = LineCol(code, *position)

    while end < p2 and not end.eof and end.char() in WHITESPACE:
        end.inc()

    if end == p2:
        return inc_tuple(end.tuple())
    return
