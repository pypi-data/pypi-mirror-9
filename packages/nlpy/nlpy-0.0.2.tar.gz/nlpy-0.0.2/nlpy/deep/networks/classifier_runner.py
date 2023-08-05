#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 NLPY.ORG
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl.html

from basic_nn import NeuralNetwork
import theano
import theano.tensor as T

class NeuralClassifierRunner(NeuralNetwork):
    '''A classifier attempts to match a 1-hot target output.'''

    def __init__(self, config):
        super(NeuralClassifierRunner, self).__init__(config)

    def setup_vars(self):
        super(NeuralClassifierRunner, self).setup_vars()

        # for a classifier, k specifies the correct labels for a given input.
        self.vars.k = T.ivector('k')
        self.inputs.append(self.vars.k)

    @property
    def cost(self):
        return T.constant(0)

    @property
    def errors(self):
        return T.constant(0)

    @property
    def monitors(self):
        return []

    def classify(self, x):
        return self.predict(x).argmax(axis=1)