"""
    Copyright (C) 2015  Evtushenko Georgy
    Authors: Evtushenko Georgy
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


def get_iris():
    """
    Load https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data
    """
    with open('./data/iris.data', 'r') as handle:
        data = [x.rstrip() for x in handle.readlines()]

    inp = []
    tgt = []
    for i in data:
        if i.find(',') != -1:
            str_l = i.split(',')
            inp.append([float(x) for x in str_l[:-1]])

            if str_l[-1] == 'Iris-setosa':
                tgt.append([1.0, 0.0, 0.0])
            elif str_l[-1] == 'Iris-versicolor':
                tgt.append([0.0, 1.0, 0.0])
            else:
                tgt.append([0.0, 0.0, 1.0])

    return inp, tgt
