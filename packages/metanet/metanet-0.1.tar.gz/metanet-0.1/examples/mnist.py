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

from metanet.networks.artificial_networks.feedforward_network import FeedforwardNetwork
from metanet.datasets import mnist
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--train', default='true')
    args = parser.parse_args()

    inp, tgt = mnist.get_mnist(10)
    net = FeedforwardNetwork(len(inp[0]), [len(inp[0])], len(tgt[0]))

    if args.train == 'true':
        for i in range(50):
            print(" [*] Epoch:", i, 'error:', net.train(inp, tgt, 1))
    else:
        net.load_net('./data/net.pkl')

    err = 0
    for i in range(len(tgt)):
        ans = net.test(inp[i])

        if tgt[i].index(max(tgt[i])) != ans.index(max(ans)):
            err += 1

    if args.train == 'true':
        net.save_net('./data/net.pkl')
    print(' [*]', err, 'errors')
