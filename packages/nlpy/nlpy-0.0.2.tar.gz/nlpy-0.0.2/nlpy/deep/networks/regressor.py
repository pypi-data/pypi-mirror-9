#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 NLPY.ORG
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl.html
from theano import tensor as T, tensor
from nlpy.deep import NeuralNetwork


class NeuralRegressor(NeuralNetwork):
    '''A regressor attempts to produce a target output.'''

    def setup_vars(self):
        super(NeuralRegressor, self).setup_vars()

        # the k variable holds the target output for input x.
        self.vars.k = T.matrix('k')
        self.inputs.append(self.vars.k)

    @property
    def cost(self):
        err = self.vars.y - self.vars.k
        return T.mean((err * err).sum(axis=1))


class SimpleRegressor(NeuralNetwork):
    '''A regressor attempts to produce a target output.'''

    def setup_vars(self):
        super(SimpleRegressor, self).setup_vars()

        # the k variable holds the target output for input x.
        self.vars.k = T.dvector('k')
        self.inputs.append(self.vars.k)

    @property
    def cost(self):
        err = self.vars.y[:, 0] - self.vars.k
        return T.mean(err * err)