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

import os, struct
from array import array as pyarray
from numpy import append, array, int8, uint8, zeros
import numpy as np


def load_mnist(dataset="training", digits=np.arange(10), path="./data/"):
    """
    Loads MNIST files into 3D numpy arrays

    Adapted from: http://abel.ee.ucla.edu/cvxopt/_downloads/mnist.py
    """

    if dataset == "training":
        fname_img = os.path.join(path, 'train-images.idx3-ubyte')
        fname_lbl = os.path.join(path, 'train-labels.idx1-ubyte')
    elif dataset == "testing":
        fname_img = os.path.join(path, 't10k-images.idx3-ubyte')
        fname_lbl = os.path.join(path, 't10k-labels.idx1-ubyte')
    else:
        raise ValueError("dataset must be 'testing' or 'training'")

    flbl = open(fname_lbl, 'rb')
    magic_nr, size = struct.unpack(">II", flbl.read(8))
    lbl = pyarray("b", flbl.read())
    flbl.close()

    fimg = open(fname_img, 'rb')
    magic_nr, size, rows, cols = struct.unpack(">IIII", fimg.read(16))
    img = pyarray("B", fimg.read())
    fimg.close()

    ind = [k for k in range(size) if lbl[k] in digits]
    N = len(ind)

    images = zeros((N, rows, cols), dtype=uint8)
    labels = zeros((N, 1), dtype=int8)

    for i in range(len(ind)):
        images[i] = array(img[ind[i]*rows*cols: (ind[i]+1)*rows*cols]).reshape((rows, cols))
        labels[i] = lbl[ind[i]]

    inp = []
    tgt = []
    for i in range(len(ind)):
        inp.append(images[i].reshape(-1)/float(255))  # Scale img to 0.0 - 1.0 range

        out = [0.0] * 10
        out[labels[i][0]] = 1.0
        tgt.append(out)
    return inp, tgt


def get_mnist(num_of_pair, dir_path='./data/'):
    print(' [*] Start loading MNIST')
    inp, tgt = load_mnist(path=dir_path)
    print(' [*]', num_of_pair, 'pair was loaded')
    print(' [*] Stop loading MNIST')
    return inp[0:num_of_pair], tgt[0:num_of_pair]
