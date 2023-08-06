"""
    A program demonstrate how opposite neural networks work.
    Visit http://evtushenko.turris-eburnea.ru/opp_ann_2014.html
    for more details.
"""

__author__ = 'Evtushenko Georgy'

from metanet.networks.artificial_networks.opposed_network import OpposedNetwork
from metanet.datasets.xor import get_xor

if __name__ == '__main__':
    inp, tgt = get_xor()

    net = OpposedNetwork(2, [4], 1)

    for i in range(100):
        print(net.train(inp, tgt, 1))

    net.select_net(inp, tgt)

    print('\n\t[*]', net.test([1.0, 0.0]))

    #net.draw_net()
