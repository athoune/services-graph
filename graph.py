#!/usr/bin/env python

import networkx as nx
import yaml
import matplotlib.pyplot as plt
import seaborn as sns


class Service(object):

    def __init__(self, name, conf):
        self.name = name
        self.conf = conf
        self.links = [a.split(':')[0] for a in conf.get('links', [])]
        self.type = conf.get('type', 'service')

    def __repr__(self):
        return "<%s>" % self.name


class Compose(object):

    def __init__(self, conf):
        self._g = None
        self.conf = yaml.load(conf)
        self.services = {}
        for service, value in self.conf.items():
            if value is None:
                self.services[service] = Service(service, {})
            else:
                self.services[service] = Service(service, value)

    def graph(self):
        if self._g is None:
            self._g = nx.DiGraph()
            for node in self.services.values():
                for link in node.links:
                    self._g.add_edge(self.services[link], node)
        return self._g

    def filter(self, **args):
        t, value = args.items()[0]
        return (node for node in self.graph() if
                getattr(node, t) == value)

    def by_application(self, *args):
        if len(args) == 0:
            return self.graph()
        apps = self.filter(type='application')
        nodes = set()
        for app in [a for a in apps if a.name in args]:
            n = ancestors(self.graph(), app)
            nodes |= n
        return nodes


def ancestors(digraph, node, bag=None):
    if bag is None:
        bag = set()
    for a in digraph.predecessors(node):
        bag.add(a)
        ancestors(digraph, a, bag)
    return bag


if __name__ == "__main__":
    import sys

    compose = Compose(open(sys.argv[1], 'r'))
    G = compose.graph()

    pos = nx.circular_layout(G)

    sns.set()
    palette = sns.color_palette()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    nodes = G.nodes()

    def color(node):
        if node.type == 'front':
            return 0
        if node.type == 'perf':
            return 1
        if node.type == 'application':
            return 2
        return 3

    def size(node):
        if node.type == 'application':
            return 1200
        return 600

    nx.draw(G, pos=pos,
            node_size=[size(a) for a in pos.keys()],
            node_color=[palette[color(a)] for a in pos.keys()])
    for node, po in pos.items():
        ax.annotate(None, po, backgroundcolor='white', alpha=0.5)
        ax.annotate(node.name, po, color='black')

    apps = compose.filter(type='application')
    for app in apps:
        print app, ancestors(G, app)

    print 'serviceA', compose.by_application('serviceA')
    print 'serviceB', compose.by_application('serviceB')
    print 'serviceB + worker', compose.by_application('serviceB', 'worker')

    plt.show()
