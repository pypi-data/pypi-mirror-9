from unittest import TestCase

from metanet.networks.artificial_networks.feedforward_network import FeedforwardNetwork
from metanet.networks.metanet import MetaNet
from metanet.datasets.xor import get_xor

import networkx as nx

#import matplotlib.pyplot as plt

if __name__=='__main__':
    inp, tgt = get_xor()

    out_net = FeedforwardNetwork(2, [4], 2)
    inp_net_1 = FeedforwardNetwork(2, [4], 2)
    inp_net_2 = FeedforwardNetwork(2, [4], 2)

    out_net.name = 'out'
    inp_net_1.name = 'inp1'
    inp_net_2.name = 'inp2'

    tgt_1 = [[0.0, 0.0], [1.0, 0.0], [1.0, 0.0], [0.0, 0.0]]
    tgt_2 = [[0.0, 0.0], [0.0, 1.0], [0.0, 1.0], [0.0, 0.0]]

    for i in range(500):
        print("OutNet err: {:4.4f}".format(out_net.train(inp, tgt_1, 1)[0]),
              "InpNet1 err: {:4.4f}".format(inp_net_1.train(inp, tgt_1, 1)[0]),
              "InpNet2 err: {:4.4f}".format(inp_net_2.train(inp, tgt_2, 1)[0]))


    metanet = MetaNet()
    metanet.add_input_net(inp_net_1)
    metanet.add_input_net(inp_net_2)
    metanet.add_output_net(out_net)

    metanet.connect_nets(inp_net_1, out_net)
    metanet.connect_nets(inp_net_2, out_net)
    metanet.connect_nets(out_net, inp_net_1)
    metanet.connect_nets(out_net, inp_net_2)

    print("\nIntNet1 input = [1.0, 0.0], InpNet2 input = [0.0, 0.0]")
    print('-'*10)
    print("OutNet output = {:4.4f}".format(metanet.test([[1.0, 0.0], [0.0, 0.0]], log_file='log.txt')[0][0]))
    #metanet.simulate([[1.0, 0.0], [0.0, 0.0]], max_inter=4, log_file='log.txt')
    print("Must be -> 0.0")

    #metanet.draw_metanet()
    #out_net.draw_net()