## @file hopfield_network.py
#  HopfieldNetwork implementation
#  Логика обучения была взята из https://github.com/pmatigakis/hopfieldnet

## @package artificial_networks

#  @author Evtushenko Georgy
#  @date 05/03/2015 17:19:00
#  @version 1.1

## @mainpage Metanet documentation
#  @section intro_sec Introduction
#  Short script to demonstrate the use of doxygen.
#
#  @section license_sec License
#\verbatim  This file is part of MetaNet.
#
#  MetaNet is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MetaNet is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MetaNet.  If not, see <http://www.gnu.org/licenses/>.
#
# (Этот файл — часть MetaNet.
#
#  MetaNet - свободная программа: вы можете перераспространять ее и/или
#  изменять ее на условиях Стандартной общественной лицензии GNU в том виде,
#  в каком она была опубликована Фондом свободного программного обеспечения;
#  либо версии 3 лицензии, либо (по вашему выбору) любой более поздней
#  версии.
#
#  MetaNet распространяется в надежде, что она будет полезной,
#  но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА
#  или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной
#  общественной лицензии GNU.
#
#  Вы должны были получить копию Стандартной общественной лицензии GNU
#  вместе с этой программой. Если это не так, см.
#  <http://www.gnu.org/licenses/>.)
#\endverbatim

__author__ = 'Evtushenko Georgy'

from ..nodes.neuron import SignNeuron
from ..nodes.network import Network
from ..groups.group import Group

import networkx as nx
import numpy as np


class HopfieldNetwork(Network):
    def __init__(self, size):
        self.create_graph(size, SignNeuron)
        self.weights = np.random.uniform(-1.0, 1.0, (size, size))

    def create_graph(self, input_size, neuron_type):
        self.layers = []

        self.graph = nx.MultiDiGraph()

        self.layers.append(Group(input_size, lambda x: neuron_type()))
        for neuron in self.layers[-1].get_nodes():
            self.graph.add_node(neuron)

    def set_layer_state(self, layer, inputs):
        neurons = self.layers[layer].get_nodes()
        for idx in range(len(neurons)):
            neurons[idx].x = inputs[idx]

    def set_input_state(self, inputs):
        self.set_layer_state(0, inputs)

    def get_layer_state(self, layer: int):
        return [neuro.x for neuro in self.layers[layer].get_nodes()]

    def get_out_state(self):
        return self.get_layer_state(len(self.layers) - 1)

    def evaluate(self, input_pattern):
        """Calculate the output of the network using the input data"""
        sums = input_pattern.dot(self.weights)

        neurons = self.layers[-1].get_nodes()

        for i, value in enumerate(sums):
            neurons[i].calc(value)

        return self.get_out_state()

    def test(self, input_pattern, max_iterations=10):
        """Run the network using the input data until the output state doesn't change
        or a maximum number of iteration has been reached."""
        last_input_pattern = np.array(input_pattern)

        iteration_count = 0

        while True:
            result = self.evaluate(last_input_pattern)

            iteration_count += 1

            if np.array_equal(result, last_input_pattern) or iteration_count == max_iterations:
                return result
            else:
                last_input_pattern = np.array(result)

    def train(self, input_patterns):
        """Train a network using the Hebbian learning rule"""
        n = len(input_patterns)

        num_neurons = self.weights.shape[0]

        weights = np.zeros((num_neurons, num_neurons))

        for i in range(num_neurons):
            for j in range(num_neurons):
                if i == j: continue
                for m in range(n):
                    weights[i, j] += input_patterns[m][i] * input_patterns[m][j]

        weights *= 1/float(n)

        self.weights = weights

    def draw_net(self):
        import matplotlib.pyplot as plt

        position = dict()

        for i, layer in enumerate(self.layers):
            for j, neuron in enumerate(layer.get_nodes()):
                position[neuron] = (i, float(j)/len(layer))

        nx.draw(self.graph, position)
        plt.show()