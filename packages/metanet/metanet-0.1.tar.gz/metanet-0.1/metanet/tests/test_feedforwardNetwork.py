from unittest import TestCase

from networks.artificial_networks.feedforward_network import FeedforwardNetwork
from datasets.xor import get_xor

import networkx as nx

import matplotlib.pyplot as plt

class TestFeedforwardNetwork(TestCase):
    def test_all(self):
        net = FeedforwardNetwork(7, [1, 2, 3], 7)

        self.assertEqual(net.get_input_size(), 7)
        self.assertEqual(net.get_output_size(), 7)

        net.set_layer_state(0, [1.0]*7)

        self.assertEqual(net.get_layer_state(0)[0], 1.0)

        #nx.draw(net.graph)
        #plt.show()