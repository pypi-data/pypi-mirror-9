#  @file neuron.py
#  Neuron implementation

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

from abc import abstractmethod

import numpy as np
import random
import math


## Neuron class.
#<p>Класс определяющий интерфейсы нейронов.</p>
class Neuron(Node):
    """Abstract class of network (interface)
    """
    def __init__(self, prev_layer_size=0):
        self.x = 0.0
        self.e = 0.0
        self.dw = 0.0

        if prev_layer_size > 0:
            self.w = np.array([random.uniform(-0.2, 0.2) for _ in range(prev_layer_size)])

        super().__init__()

    ## Определение выходного состояния
    #  <p>По изменении состояния нейрона необходимо вызывать 
    #  метод self.check_predicates если вы хотите иметь возможность
    #  подписывать события к вашему типу нейрона</p>
    #  @param self Указатель на объект.
    #  @param inp Массив входных сигналов в порядке определения весов.
    @abstractmethod
    def calc(self, inp):
        pass

    @abstractmethod
    def derivative(self, inp):
        pass


## SigmoidNeuron class.
#<p>Класс определяющий интерфейсы нейронов с сигмоидальной функцией
#  активации.</p>
class SigmoidNeuron(Neuron):
    ## Функция активации \f$ \frac{1}{1+e^{-x}} \f$
    def calc(self, inp: np.array):
        s = np.sum(inp * self.w)
        self.x = 1.0/(1.0 + math.exp(-1 * s))
        self.check_predicates()

    def derivative(self, inp):
        return (1.0 - inp) * inp


## TanhNeuron class.
#<p>Класс определяющий интерфейсы нейронов с функцией
#  активации - гиперболический тангенс.</p>
class TanhNeuron(Neuron):
    ## Функция активации \f$ tanh(x) \f$
    def calc(self, inp):
        s = np.sum(inp * self.w)
        self.x = math.tanh(s)
        self.check_predicates()

    def derivative(self, inp):
        return 1 - inp ** 2


## LinearNeuron class.
#<p>Класс определяющий интерфейсы нейронов с линейной
#  функцией активации.</p>
#  @todo Доработать этот класс.
class LinearNeuron(Neuron):
    """
    ???
    """
    k = 0.8
    def calc(self, inp):
        self.x = np.sum(inp)

    def derivative(self, inp):
        return self.k