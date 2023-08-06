#  @file node.py
#  Node implementation

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

from abc import ABCMeta, abstractmethod

## Node class.
#<p>Класс определяющий интерфейсы всех узлов - нейронов,
#  сетей, метасетей. Для хранения в networkx необходима реализация
#  ряда методов. Отвечает за присвоение уникального идентификатора
#  элементам библиотеки. Реализует механизм выплнения подписываемых
#  функций при срабатывании предиката. В нейронах проверка предикатов
#  происходит при применении функции активации, в сетях - при
#  изменении выходного сигнала, в метасетях - при расчёте сетей.</p>
class Node(object):
    """Abstract class of network node (interface)
    """
    __metaclass__ = ABCMeta
    counter=0

    def __init__(self):
        Node.counter += 1
        self.id = Node.counter
        self.name = ''
        self.do_when_activate = []

    def add_action_on_active(self, function, unary_predicate):
        self.do_when_activate.append([function, unary_predicate])

    def check_predicates(self):
        for func, pred in self.do_when_activate:
            if pred(self):
                func(self)

    def get_name(self):
        if not self.name:
            return self.id
        else:
            return self.name

    @abstractmethod
    def get_out_state(self):
        pass

    def __eq__(self, other):
        if isinstance(other, Node):
            return other.id == self.id
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)