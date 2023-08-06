from unittest import TestCase

from metanet.networks.artificial_networks.feedforward_network import FeedforwardNetwork
from metanet.networks.metanet import MetaNet
from metanet.datasets.xor import get_xor

import networkx as nx


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

    metanet.name = 'MetaNet'

    metanet.add_action_on_active(lambda x: print(x.get_name(), 'activation found'),
                                 lambda net: net.get_out_state()[0][0] > 0.4)

    inp_net_1.add_action_on_active(lambda x: print(x.get_name(),
                                                   'net has ',
                                                   x.get_layer_state(0)[0],
                                                   'on input fist neuron'),
                                   lambda net: net.get_layer_state(0)[0] > 0.4)

    print("\nIntNet1 input = [1.0, 0.0], InpNet2 input = [0.0, 0.0]")
    print('-'*10)
    print("OutNet output = {:4.4f}".format(metanet.test([[1.0, 0.0], [0.0, 0.0]])[0][0]))
    print("Must be -> 0.0")

    #metanet.draw_metanet()
    #out_net.draw_net()