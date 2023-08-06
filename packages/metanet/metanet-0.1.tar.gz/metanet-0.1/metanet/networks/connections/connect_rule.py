"""
    This file is part of MetaNet.

    MetaNet is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    MetaNet is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with MetaNet.  If not, see <http://www.gnu.org/licenses/>.

  (Этот файл — часть MetaNet.

   MetaNet - свободная программа: вы можете перераспространять ее и/или
   изменять ее на условиях Стандартной общественной лицензии GNU в том виде,
   в каком она была опубликована Фондом свободного программного обеспечения;
   либо версии 3 лицензии, либо (по вашему выбору) любой более поздней
   версии.

   MetaNet распространяется в надежде, что она будет полезной,
   но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА
   или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной
   общественной лицензии GNU.

   Вы должны были получить копию Стандартной общественной лицензии GNU
   вместе с этой программой. Если это не так, см.
   <http://www.gnu.org/licenses/>.)
"""

__author__ = 'Evtushenko Georgy'

from ..groups.group import Group

import networkx as nx


def FullConnection(group1: Group, group2: Group, graph: nx.MultiDiGraph):
    for node in group1.get_nodes():
        graph.add_node(node)
    for node in group2.get_nodes():
        graph.add_node(node)

    for i in group1.get_nodes():
        for j in group2.get_nodes():
            graph.add_edge(i, j)


def InjectConnection(group1: Group, group2: Group, graph: nx.MultiDiGraph):
    neuron_group_1 = group1.get_nodes()
    neuron_group_2 = group2.get_nodes()

    if len(neuron_group_1) != len(neuron_group_2):
        raise Exception('Size of group do not match for inject connection')

    for node in neuron_group_1:
        graph.add_node(node)
    for node in neuron_group_2:
        graph.add_node(node)

    for i in range(len(neuron_group_1)):
        graph.add_edge(neuron_group_1[i], neuron_group_2[i])