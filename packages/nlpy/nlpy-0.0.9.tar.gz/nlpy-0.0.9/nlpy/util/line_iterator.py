#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 NLPY.ORG
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl.html

class LineIterator(object):

    def __init__(self, path):
        self._path = path

    def __iter__(self):
        return (line.strip() for line in open(self._path).xreadlines())