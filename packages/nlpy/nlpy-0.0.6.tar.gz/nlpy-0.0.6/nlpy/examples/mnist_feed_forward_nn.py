#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 NLPY.ORG
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl.html

from nlpy.dataset import MnistDataset, HeartScaleDataset, MiniBatches
from nlpy.deep.conf import NetworkConfig, TrainerConfig
from nlpy.deep import NeuralLayer, NeuralClassifier, NeuralRegressor, SGDTrainer
import theano
import logging
import time
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    net_conf = NetworkConfig(input_size=28*28)
    net_conf.layers = [NeuralLayer(500, 'sigmoid'), NeuralLayer(10, 'softmax')]

    trainer_conf = TrainerConfig()
    trainer_conf.learning_rate = 0.01
    trainer_conf.weight_l2 = 0.0001
    trainer_conf.hidden_l2 = 0.0001

    network = NeuralClassifier(net_conf)
    trainer = SGDTrainer(network)

    mnist = MiniBatches(MnistDataset(target_format='number'), batch_size=20)

    start_time = time.time()
    for k in list(trainer.train(mnist.train_set(), mnist.valid_set(), test_set=mnist.test_set())):
        pass
    print k
    trainer.test(0, mnist.test_set())
    end_time = time.time()
    print "elapsed time:", (end_time - start_time) / 60, "mins"