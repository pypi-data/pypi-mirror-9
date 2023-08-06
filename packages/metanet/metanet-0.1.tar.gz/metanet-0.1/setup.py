__author__ = 'Evtushenko Georgy'

from setuptools import setup, find_packages

setup(
    name="metanet",
    version="0.1",
    description="Free portable library for meta neural network research",
    license="GPL3",
    packages=['metanet', 'metanet.datasets', 'metanet.networks', 'metanet.networks.nodes', 'metanet.networks.artificial_networks', 'metanet.networks.nodes', 'metanet.networks.groups', 'metanet.networks.connections'],
    install_requires=['numpy', 'networkx'],
)
