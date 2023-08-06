#  @file metanet.py
#  Metanet implementation

## @package networks

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
import logging
import json

from .artificial_networks.feedforward_network import FeedforwardNetwork
from .connections.connect_rule import FullConnection
from .nodes.network import Network
from .groups.group import Group


## MetaNet class.
#<p>Класс определяющий метасетевую структуру.
#  Как и остальные узлы библиотеки, МетаСеть позволяет
#  привязывать события к предикатам определяемым пользователем.</p>
#  @todo <p>Доработать механизмы связи сетей (по нейронам/
#  автодополнение нулями недостающих входов)</p>
class MetaNet(Network):
    def __init__(self):
        self.net_graph = nx.DiGraph()
        self.input_layer = []
        self.output_layer = []
        self.hidden_layer = []

        super().__init__()

    ## Добавить входную нейронную сеть
    #  <p>Необходимо учитывать порядок сети при добавлении, т.к. при вызове функции
    #  моделирования или теста передается массив входов для сетей и устанавливаются
    #  они по порядку в массиве self.input_layer </p>
    #  @param self Указатель на объект.
    #  @param net Входная НС.
    def add_input_net(self, net):
        self.input_layer.append(net)
        self.net_graph.add_node(net)

    ## Добавить выходную нейронную сеть
    #  <p>Необходимо учитывать порядок сети при добавлении, т.к. при вызове функции
    #  моделирования или теста возвращаются значения в порядке, определенном в
    #  self.output_layer.</p>
    #  @param self Указатель на объект.
    #  @param net Выходная НС.
    def add_output_net(self, net):
        self.output_layer.append(net)
        self.net_graph.add_node(net)

    ## Добавить скрытую нейронную сеть
    #  @param self Указатель на объект.
    #  @param net Скрытая НС.
    def add_hidden_net(self, net):
        self.hidden_layer.append(net)
        self.net_graph.add_node(net)

    def add_net(self, net):
        self.net_graph.add_node(net)

    ## Добавить связь между НС
    #  @param self Указатель на объект.
    #  @param net Сеть источник.
    #  @param net Сеть приемник.
    #  @todo Добавить возможность задания правила связей
    def connect_nets(self, net1, net2):
        if net1.get_output_size() != net2.get_input_size():
            raise Exception("Networks do not match")
        self.net_graph.add_edge(net1, net2)

    ## Добавить массив связей между НС-ми
    #  @param self Указатель на объект.
    #  @todo Доработать протокол использования данного метода.
    def set_connections(self, connections):
        for connect in connections:
            self.connect_nets(connect[0], connect[1])

    ## Возвращает число связей НС
    def get_edges_num(self):
        return len(self.net_graph.edges())

    ## Прогнать сигнал по метасети.
    #  Работает до момента активации всех НС (или определённое число шагов)
    #  @param self Указатель на объект.
    #  @param inp Входы для всех входных НС.
    #  @param max_iter Максимальное число итераций - не обязательный параметр.
    #  @param log_file Имя файла для вывода лога. Если файл не указан - лог не ведется.
    #  @return Выходной сигнал всех нейронных сетей (НС)
    def test(self, inp, max_inter=None, log_file=''):
        return self.simulate(inp, max_inter, log_file, until_output_not_ready=True)

    ## Прогнать сигнал по метасети.
    #  @param self Указатель на объект.
    #  @param inp Входы для всех входных НС.
    #  @param max_iter Максимальное число итераций - не обязательный параметр.
    #  @param log_file Имя файла для вывода лога. Если файл не указан - лог не ведется.
    #  @param until_output_not_ready Указывает сети работать до активации всех выходных НС
    #  @return Выходной сигнал всех нейронных сетей (НС)
    def simulate(self, inp, max_inter=None, log_file='', until_output_not_ready=False):
        if log_file:
            logging.basicConfig(filename=log_file, level=logging.DEBUG,
                                format='%(asctime)s %(message)s',
                                datefmt='%m/%d/%Y %I:%M:%S %p')
            logging.info('='*10 + ' simulation started ' + '='*10)

        if len(inp) != len(self.input_layer):
            raise Exception('Cant set input vector for this metanet (size do not match)')
        # set inputs for all nets to zero
        for net in self.net_graph.nodes():
            net.set_layer_state(0, [0.0] * net.get_input_size())
        for i in range(len(inp)):
            self.input_layer[i].set_layer_state(0, inp[i])

        nets_to_calc = self.input_layer[:]
        output_ready = [False for _ in self.output_layer]

        # run until all output networks not calc
        # or count < max_inter
        count = 0
        while len(nets_to_calc) > 0:
            if max_inter != None:
                if count >= max_inter:
                    return self.get_out_state()

            if log_file:
                log_str = '-'*5 + 'slice %s' % count + '-'*5
                logging.info(log_str)

            calced = dict()
            for i in nets_to_calc:
                calced[i] = False

            for net in nets_to_calc[:]:
                if calced[net]:
                    continue

                calced[net] = True

                successors_input = net.test()

                self.check_predicates()

                net.set_input_state([0.0] * net.get_input_size())  # input signal die after 1 tact

                if log_file:
                    logging.info(' - Net %s calced. Out state %s'%
                    (net.get_name(), json.dumps(self.get_out_state())))

                while net in nets_to_calc: nets_to_calc.remove(net)

                if until_output_not_ready:
                    if net in self.output_layer:
                        output_ready[self.output_layer.index(net)] = True
                    if False not in output_ready:
                        return self.get_out_state()

                for successor in self.net_graph.successors(net):
                    nets_to_calc.append(successor)

                    prev_state = successor.get_layer_state(0)

                    for idx, i in enumerate(prev_state):
                        if i > 0.45:
                            successors_input[idx] = max(i, successors_input[idx])
                        else:
                            pass

                    successor.set_layer_state(0, successors_input)

                if max_inter != None:
                    if count != max_inter:
                        net.set_out_state([0.0] * net.get_output_size())  # input signal die after 1 tact

            count += 1

        return self.get_out_state()

    ## Возвращает массив состояний выходных сетей
    #  <p>Необходимо учитывать порядок сети, т.к. индекс данных сети 
    #  зависит от порядка в массиве self.input_layer </p>
    #  @param self Указатель на объект.
    #  @return Массив состояний выходных НС
    def get_out_state(self):
        return [result.get_out_state() for result in self.output_layer]

    ## Прогнать сигнал по метасети.
    #  Отображает граф связей метасети. Петли не отображаются.
    #  @param self Указатель на объект.
    #  @todo Изучить pygraphviz - для отображения петель.
    def draw_metanet(self):
        import matplotlib.pyplot as plt

        i = 0
        position = dict()

        print(len(self.input_layer))
        for j, net in enumerate(self.input_layer):
            position[net] = (i, float(j)/len(self.input_layer))

        i += 1
        for j, net in enumerate(self.output_layer):
            position[net] = (i, float(j)/len(self.output_layer))

        nx.draw(self.net_graph, position)
        plt.show()