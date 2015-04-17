#!/usr/bin/env python

import networkx as nx
import yaml
import matplotlib.pyplot as plt


class Service(object):

    def __init__(self, name, conf):
        self.name = name
        self.conf = conf
        self.links = [a.split(':')[0] for a in conf.get('links', [])]
        self.type = conf.get('type', 'service')


class Compose(object):

    def __init__(self, conf):
        self.conf = yaml.load(conf)
        self.services = {}
        for service, value in self.conf.items():
            if value is None:
                self.services[service] = Service(service, {})
            else:
                self.services[service] = Service(service, value)

    def graph(self):
        g = nx.DiGraph()
        for node in self.services.values():
            for link in node.links:
                g.add_edge(self.services[link], node)
        return g


if __name__ == "__main__":
    import sys

    compose = Compose(open(sys.argv[1], 'r'))
    G = compose.graph()

    pos = nx.circular_layout(G)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    nodes = G.nodes()

    def color(node):
        if node.type == 'front':
            return 'yellow'
        if node.type == 'perf':
            return 'blue'
        if node.type == 'application':
            return 'green'
        return 'red'

    def size(node):
        if node.type == 'application':
            return 1200
        return 600

    nx.draw(G, pos=pos,
            node_size=[size(a) for a in pos.keys()],
            node_color=[color(a) for a in pos.keys()])
    for node, po in pos.items():
        ax.annotate(None, po, backgroundcolor='white', alpha=0.5)
        ax.annotate(node.name, po, color='black')

    plt.show()
