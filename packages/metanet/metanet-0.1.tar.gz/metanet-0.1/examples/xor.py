from metanet.networks.artificial_networks.feedforward_network import FeedforwardNetwork
from metanet.datasets.xor import get_xor

inp, tgt = get_xor()
net = FeedforwardNetwork(len(inp[0]), [4], len(tgt[0]))

net.eta = 0.45

for i in range(10000):
	print(net.train(inp, tgt, 1)[0])
