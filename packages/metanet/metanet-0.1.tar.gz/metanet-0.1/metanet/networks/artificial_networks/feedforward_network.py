#  @file feedforward_network.py
#  FeedforwardNetwork implementation

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

import networkx as nx
import numpy as np
import math

from ..connections.connect_rule import FullConnection
from ..nodes.neuron import SigmoidNeuron, TanhNeuron, LinearNeuron
from ..nodes.network import Network
from ..groups.group import Group


## FeedforwardNetwork class.
#<p>Класс нейронной сети прямого распространения (многослойный персептрон).
#  Сеть позволяет использовать разные типы нейронов даже в одном слое.</p>
#  @todo При соединении сетей добавить проверку на циклические связи
class FeedforwardNetwork(Network):
    ## Конструктор многослойного персептрона
    #  @param self Указатель на объект.
    #  @param input_size Число входных нейронов.
    #  @param hidden_sizes Список размеров скрытых слоев.
    #  @param output_size Число выходных нейронов.
    #  @param neuron_type Тип нейронов сети. 
    #  @param eta Шаг обучения 
    #  @param alpha Момент
    def __init__(self, input_size, hidden_sizes, output_size, neuron_type=TanhNeuron, eta=0.15, alpha=0.15):
        self.create_graph(input_size, hidden_sizes, output_size, neuron_type)
        self.eta = eta
        self.alpha = alpha

        super().__init__()

    def create_graph(self, input_size, hidden_sizes, output_size, neuron_type):
        self.layers = []

        self.graph = nx.MultiDiGraph()

        self.layers.append(Group(input_size, lambda x: neuron_type()))
        # create hidden layer with W size = prev neurons number
        for size in hidden_sizes:
            self.add_next_layer(size, neuron_type)
        self.add_next_layer(output_size, neuron_type)

    def add_next_layer(self, layer_size, Type):
        self.layers.append(Group(layer_size, lambda x: Type(self.layers[-1].get_size())))
        FullConnection(self.layers[-2], self.layers[-1], self.graph)

    def forward(self, inputs=None):
        # Copy inputs
        if inputs != None:
            inp_neurons = self.layers[0].get_nodes()

            for i in range(len(inputs)):
                inp_neurons[i].x = inputs[i]
        # Propagate signal
        # for i in range(1, len(self.layers)):
        #    for neuron in self.layers[i].get_nodes():
        #        neuron.calc(np.array([n.x for n in self.graph.predecessors(neuron)]))
        # Propagate signal
        for i in range(1, len(self.layers)):
            for neuron in self.layers[i].get_nodes():
                pre_nodes = self.layers[i - 1].get_nodes()
                neuron.calc(np.array([n.x for n in pre_nodes]))
        self.check_predicates()

    def adjust_weights(self):
        for i in range(1, len(self.layers)):
            neurons = self.layers[i].get_nodes()
            for j in range(len(neurons)):
                pre_neurons = self.layers[i - 1].get_nodes()
                for k in range(len(pre_neurons)):
                    x = pre_neurons[k].x
                    e = neurons[j].e
                    dw = neurons[j].dw

                    neurons[j].w[k] += self.eta * x * e + self.alpha * dw
                    neurons[j].dw = self.eta * x * e

    def back_prop(self, target):
        # Compute output error
        mse = 0.0
        mae = 0.0

        out_neurons = self.layers[-1].get_nodes()
        for i in range(len(out_neurons)):
            x = out_neurons[i].x
            d = target[i] - x

            # can use different function for neurons
            out_neurons[i].e = d * out_neurons[i].derivative(x)
            mse += d * d
            mae += math.fabs(d)

        mse /= len(self.layers[-1].get_nodes())
        mae /= len(self.layers[-1].get_nodes())

        # backpropagation
        for i in list(reversed(range(0, len(self.layers) - 1))):
            neurons = self.layers[i].get_nodes()
            for j in range(len(neurons)):
                x = neurons[j].x
                e = 0.0

                post_neurons = self.layers[i + 1].get_nodes()
                for k in range(len(post_neurons)):
                    e += post_neurons[k].w[j] * post_neurons[k].e
                neurons[j].e = neurons[j].derivative(x) * e

        return mse, mae

    def train(self, inputs, targets, epoch):
        err = []
        count = 0
        while epoch > count:
            mae = 0.0
            for i in range(len(targets)):
                self.forward(inputs[i])
                _, er = self.back_prop(targets[i])
                mae += er
                self.adjust_weights()

            err.append(mae/len(targets))
            count += 1
        return err

    def test(self, inp=None):
        self.forward(inp)
        return self.get_layer_state(len(self.layers) - 1)

    def set_layer_state(self, layer, inputs):
        neurons = self.layers[layer].get_nodes()
        for idx in range(len(neurons)):
            neurons[idx].x = inputs[idx]

    def set_input_state(self, inputs):
        self.set_layer_state(0, inputs)

    def set_out_state(self, inputs):
        self.set_layer_state(len(self.layers) - 1, inputs)

    def get_layer_state(self, layer: int):
        return [neuro.x for neuro in self.layers[layer].get_nodes()]

    def get_out_state(self):
        return self.get_layer_state(len(self.layers) - 1)

    def get_input_size(self):
        return len(self.layers[0].get_nodes())

    def get_output_size(self):
        return len(self.layers[-1].get_nodes())

    def draw_net(self):
        import matplotlib.pyplot as plt

        position = dict()

        for i, layer in enumerate(self.layers):
            for j, neuron in enumerate(layer.get_nodes()):
                position[neuron] = (i, float(j)/len(layer))

        nx.draw(self.graph, position)
        plt.show()