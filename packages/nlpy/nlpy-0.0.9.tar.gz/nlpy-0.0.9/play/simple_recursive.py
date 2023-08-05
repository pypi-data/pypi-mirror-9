#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 NLPY.ORG
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl.html

import unittest
import time, os, sys
from nlpy.lm import Vocab
from nlpy.lm.data_generator import RNNDataGenerator
from nlpy.util import internal_resource

from nlpy.deep import NetworkConfig, TrainerConfig, NeuralClassifier, SGDTrainer, AdaDeltaTrainer, AdaGradTrainer
from nlpy.deep.functions import FLOATX, monitor_var as MV, plot_hinton
from nlpy.deep.networks import NeuralLayer
from nlpy.deep.networks.recursive import RAELayer, GeneralAutoEncoder
from nlpy.deep.networks.classifier_runner import NeuralClassifierRunner
from nlpy.util import LineIterator, FakeGenerator
from collections import Counter
import copy
import numpy as np
import random as rnd

import logging
logging.basicConfig(level=logging.INFO)

random = rnd.Random(3)

"""
Simple RAE data
"""


def build_vectors(size):
    data = []
    for i in range(size):
        d = np.eye(1, size, k=i)[0]
        data.append(d)
    return data


def build_data(vectors, amount):
    data = []
    for i in range(amount):
        d = copy.deepcopy(vectors)
        random.shuffle(d)
        data.append((d, ))
    return data


vectors = build_vectors(10)

train_data = build_data(vectors, 300)
valid_data = build_data(vectors, 100)

"""
Setup network
"""

model_path = "/tmp/recursive_nn1.gz"

net_conf = NetworkConfig(input_size=10)
net_conf.layers = [RAELayer(size=100)]

trainer_conf = TrainerConfig()
trainer_conf.learning_rate = 0.01
trainer_conf.weight_l2 = 0.0001
trainer_conf.hidden_l2 = 0.0001
trainer_conf.monitor_frequency = trainer_conf.validation_frequency = trainer_conf.test_frequency = 1

network = GeneralAutoEncoder(net_conf)

trainer = AdaDeltaTrainer(network, config=trainer_conf)

"""
Run the network
"""
start_time = time.time()

if os.path.exists(model_path):
    network.load_params(model_path)
    pass

# import pdb; pdb.set_trace()
# raise SystemExit

for _ in trainer.train(train_data, valid_set=valid_data):
    pass

end_time = time.time()
network.save_params(model_path)

print "elapsed time:", (end_time - start_time) / 60, "mins"

print "--- Encoding-decoding test ---"
print "Test data:"
d = valid_data[0][0]
plot_hinton(d)
rep = network.encode(d)
print "Representation:"
plot_hinton(rep)
print "Decoding result:"
res = network.decode(rep, 10)
plot_hinton(res)
