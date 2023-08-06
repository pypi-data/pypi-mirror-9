#  @file opposed_network.py
#  OpposedNetwork implementation

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

from ..artificial_networks.feedforward_network import FeedforwardNetwork
from ..nodes.neuron import SigmoidNeuron, TanhNeuron, LinearNeuron
from ..nodes.network import Network
from ..groups.group import Group


class OpposedNetwork(Network):
    ## Конструктор оппозитной сети
    #  @param self Указатель на объект.
    #  @param input_size Число входных нейронов.
    #  @param hidden_sizes Список размеров скрытых слоев.
    #  @param output_size Число выходных нейронов.
    #  @param neuron_type Тип нейронов сети.
    #  @param eta Шаг обучения
    #  @param alpha Момент
    def __init__(self, input_size, hidden_sizes, output_size,
                 neuron_type=TanhNeuron, eta=0.45, alpha=0.05):
        self.base_net = FeedforwardNetwork(input_size, hidden_sizes, output_size, neuron_type, eta, alpha)
        self.opp_net = FeedforwardNetwork(input_size, hidden_sizes, output_size, neuron_type, eta, alpha)
        self.trust_to = None

        super().__init__()

    def test(self, inp=None):
        if self.trust_to == None:
            raise Exception('Call select_net first')
        return self.trust_to.test(inp)

    def train(self, inputs, targets, epoch):
        otgt = []
        for i in targets:
            otgt.append([1.0 - i[0]])

        return self.base_net.train(inputs, targets, 1)[0], self.opp_net.train(inputs, otgt, 1)[0]

    def get_graph(self):
        graph = nx.MultiDiGraph()
        graph.add_nodes_from(self.base_net.get_graph().nodes(data=True))
        graph.add_nodes_from(self.opp_net.get_graph().nodes(data=True))
        graph.add_edges_from(self.base_net.get_graph().edges(data=True))
        graph.add_edges_from(self.opp_net.get_graph().edges(data=True))

        return graph

    def select_net(self, inputs, targets):
        otgt = []
        for i in targets:
            otgt.append([1.0 - i[0]])

        ann_maa = 0.0
        oann_maa = 0.0
        for i in range(len(inputs)):
            ann_maa += self.base_net.test(inputs[i])[0]
            oann_maa += self.opp_net.test(inputs[i])[0]

        ann_maa /= len(inputs)
        oann_maa /= len(inputs)

        # Calc dispersion
        ann_d = 0
        oann_d = 0

        for i in range(len(inputs)):
            ann_d += (self.base_net.test(inputs[i])[0] - ann_maa) ** 2
            oann_d += (self.opp_net.test(inputs[i])[0] - oann_maa) ** 2

        ann_d /= len(inputs)
        oann_d /= len(inputs)

        if ann_d > oann_d:
            self.trust_to = self.base_net
        else:
            self.trust_to = self.opp_net

    def draw_net(self):
        import matplotlib.pyplot as plt

        position = dict()

        all_layers = []
        for i, layer in enumerate(self.base_net.layers):
            all_layers.append([])

            for neuron in layer.get_nodes():
                all_layers[-1].append(neuron)
            for neuron in self.opp_net.layers[i].get_nodes():
                all_layers[-1].append(neuron)

        for i, layer in enumerate(all_layers):
            for j, neuron in enumerate(layer):
                position[neuron] = (i, float(j)/len(layer))

        nx.draw(self.get_graph(), position)
        plt.show()