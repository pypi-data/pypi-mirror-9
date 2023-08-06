#  @file network.py
#  Networks implementation

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

from .node import Node

from abc import ABCMeta, abstractmethod
import pickle


## Network class.
#<p>Класс определяющий интерфейсы сетевых структур.</p>
class Network(Node):
    """Abstract class of network (interface)
    """
    def __init__(self):
        super().__init__()

    @abstractmethod
    def test(self, inp=None, max_inter=None, log_file=''):
        pass

    @abstractmethod
    def get_graph(self):
        pass

    def save_net(self, filename):
        with open(filename, 'wb') as output:
            pickle.dump(self.__dict__, output, 2)

    def load_net(self, filename):
        with open(filename, 'rb') as handle:
            tmp_dict = pickle.load(handle)

            self.__dict__.update(tmp_dict)