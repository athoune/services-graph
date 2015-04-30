#!/usr/bin/env python

import networkx as nx
import yaml
import matplotlib.pyplot as plt
import seaborn as sns


class Service(object):
    "Service abstraction"

    def __init__(self, name, conf):
        self.name = name
        self.conf = conf
        self.links = [a.split(':')[0] for a in conf.get('links', [])]
        self.type = conf.get('type', 'service')

    def __repr__(self):
        return "<%s>" % self.name


class Compose(object):
    "Group of Services"

    def __init__(self, conf):
        self._g = None
        if type(conf) == dict:
            self.services = conf
            return
        conf = yaml.load(conf)
        self.services = {}
        for service, value in conf.items():
            if value is None:
                self.services[service] = Service(service, {})
            else:
                self.services[service] = Service(service, value)

    def __iter__(self):
        return self.services.itervalues()

    def __repr__(self):
        return "<Compose [%s]>" % ", ".join((repr(a) for a in
                                             self.services.values()))

    def __or__(self, other):
        s = self.services
        s.update(other.services)
        return Compose(s)

    def graph(self):
        if self._g is None:
            self._g = nx.DiGraph()
            for node in self.services.values():
                for link in node.links:
                    self._g.add_edge(self.services[link], node)
        return self._g

    def filter(self, f):
        return Compose(dict(((k, v) for (k, v) in self.services.iteritems()
                             if f(k, v))))


def ancestors(digraph, nodes, bag=None):
    if bag is None:
        bag = set()
    for node in nodes:
        a = digraph.predecessors(node)
        bag |= set(a)
        bag |= ancestors(digraph, a, bag)
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

    apps = compose.filter(lambda k, v: v.type == 'application')
    for app in apps:
        print app, ancestors(G, [app])
    perfs = compose.filter(lambda k, v: v.type == 'perf')
    print "apps and perfs", apps | perfs

    sA = compose.filter(lambda k, v: k == 'serviceA')
    sB = compose.filter(lambda k, v: k == 'serviceB')
    print 'serviceA', ancestors(G, sA)
    print 'serviceB', ancestors(G, sB)
    sBw = compose.filter(lambda k, v: k in
                         ('serviceB', 'worker'))
    print 'serviceB + worker', ancestors(G, sBw)

    #plt.show()
