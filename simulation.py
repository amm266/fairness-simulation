import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def value2index(vec, value):
    for i in range(len(vec)):
        if vec[i] == value:
            return i


def draw_graph(p, title="", erase=True, stop=True):
    # if erase:
    #     plt.clf()
    # if create_graph:
    # p.create_envy_graph()
    g = p.nx_graph
    pos = nx.spring_layout(g)
    ax = plt.gca()
    ax.set_title(title)
    for envy_val, color in zip((1, 2), ("blue", "red")):
        edges = [(u, v) for u, v, d in g.edges.data(data='weight') if d == envy_val]
        nx.draw_networkx_edges(g, pos=pos, edgelist=edges, edge_color=color, ax=ax)
    nx.draw_networkx_labels(g, pos=pos, ax=ax)
    nx.draw_networkx_nodes(g, pos=pos, ax=ax)
    plt.show()
    if stop:
        input()


class ChoreProblem:
    agents = 1
    items = 1
    valuation_matrix = None
    allocation = None
    envy_graph = None
    nx_graph = None
    old_allocation = dict()

    def __init__(self, agents, items):
        self.agents = agents
        self.items = items
        self.valuation_matrix = np.zeros((agents, items))
        self.allocation = np.zeros((agents, items))
        for i in range(agents):
            for j in range(items):
                self.valuation_matrix[i][j] = round(random.random(), 2)
            self.valuation_matrix[i] = np.divide(self.valuation_matrix[i], sum(self.valuation_matrix[i]))

    def get_bundle(self, s):
        if s in self.old_allocation:
            return self.old_allocation[s]
        return self.allocation[s]

    def nash_allocation(self):
        allocation = np.zeros((self.agents, self.items))
        for i in range(self.items):
            index = np.argmin(self.valuation_matrix[:, i])
            allocation[index, i] = 1
        self.allocation = allocation
        return allocation

    def valuation(self, agent, bundle=None):
        if bundle is None:
            bundle = self.get_bundle(agent)
        v = np.zeros(self.items)
        for i in range(self.items):
            v[i] = bundle[i] * self.valuation_matrix[agent, i]
        return v

    def EFX_valuation(self, agent, bundle=None):
        v = self.valuation(agent, bundle)
        if len(v[np.nonzero(v)]) == 0:
            m = 0
        else:
            m = np.min(v[np.nonzero(v)])

        return sum(v) - m

    def EF_evaluate(self, a=1, is_chore=True):
        for i in range(self.agents):
            self_v = sum(self.valuation(i))
            compare = self_v.__gt__
            if not is_chore:
                compare = self_v.__lt__
            for j in range(self.agents):
                if i == j:
                    continue
                v = sum(self.valuation(i, self.allocation[j]))
                if compare(a * v):
                    return False
        return True

    def EFX_evaluate(self, a=1):
        for i in range(self.agents):
            efx_v = self.EFX_valuation(i)
            for j in range(self.agents):
                if i == j:
                    continue
                v = sum(self.valuation(i, self.allocation[j]))
                if efx_v > a * v:
                    return False
        return True

    def create_envy_graph(self):
        self.envy_graph = np.zeros((self.agents, self.agents))
        for i in range(self.agents):
            self_v = sum(self.valuation(i))
            for j in range(self.agents):
                if i == j:
                    continue
                v = sum(self.valuation(i, self.allocation[j]))
                if self_v > v:
                    efx_v = self.EFX_valuation(i)
                    self.envy_graph[i][j] = 1
                    if efx_v > v:
                        self.envy_graph[i][j] = 2
        g = nx.from_numpy_matrix(self.envy_graph, create_using=nx.DiGraph, parallel_edges=True)
        self.nx_graph = g
        return g

    def sell_cheapest(self):
        if self.EFX_evaluate():
            return
        else:
            v1 = self.EFX_valuation(0)
            v2 = self.EFX_valuation(1)
            if v1 > sum(self.valuation(0, self.allocation[1])):
                self.transfer_cheapest_item(0, 1)
            if v2 > sum(self.valuation(1, self.allocation[0])):
                self.transfer_cheapest_item(1, 0)

    def transfer_cheapest_item(self, of, to):
        val1_array = self.valuation(of)
        min_value = np.min(val1_array[np.nonzero(val1_array)])
        min_index = value2index(val1_array, min_value)
        tmp_allocation = self.allocation.copy()
        tmp_allocation[of][min_index] = 0
        tmp_allocation[to][min_index] = 1
        self.allocation = tmp_allocation

    def strong_envy_nodes(self, s):
        bundle = np.copy(self.allocation[s])
        r = []
        for i in range(self.agents):
            self_v = self.valuation(i).sum()
            efx_other = self.EFX_valuation(i, bundle=bundle)
            if efx_other > self_v:
                r.append(i)
        r = np.array(r)
        return r


class CouponProblem(ChoreProblem):
    def examine(self):
        return (self.pool_size() < self.agents) and self.EFX_evaluate()

    def nash_allocation(self):
        allocation = np.ones((self.agents, self.items))
        for i in range(self.items):
            index = np.argmin(self.valuation_matrix[:, i])
            allocation[index, i] = 0
        self.allocation = allocation
        return allocation

    def EF_evaluate(self, a=1, is_chore=True):
        return super().EF_evaluate(a=a, is_chore=False)

    def EFX_evaluate(self, a=1):
        return len(np.where(self.envy_graph == 2)[0]) == 0

    def pool_size(self):
        return self.items * (self.agents - 1) - self.allocation.sum()

    def add_old_allocation(self, agent, bundle):
        if agent not in self.old_allocation:
            self.old_allocation[agent] = np.copy(bundle)

    def reset_old_allocation(self):
        self.old_allocation = dict()

    def create_envy_graph(self):
        self.envy_graph = np.zeros((self.agents, self.agents))
        for i in range(self.agents):
            bundle = self.get_bundle(i)
            for j in range(self.agents):
                if i == j:
                    continue
                self_v = sum(self.valuation(i, bundle=bundle))
                other_v = sum(self.valuation(i, bundle=self.allocation[j]))
                if self_v < other_v:
                    self.envy_graph[i][j] = 1
                    efx_other_v = self.EFX_valuation(i, bundle=self.allocation[j])
                    if self_v < efx_other_v:
                        self.envy_graph[i][j] = 2
        g = nx.from_numpy_matrix(self.envy_graph, create_using=nx.DiGraph, parallel_edges=True)
        self.nx_graph = g
        return g

    def source_nodes(self):
        sources = []
        for i in range(self.agents):
            if self.envy_graph[:, i].sum() == 0:
                sources.append(i)
        return sources

    def remaining_coupon(self, item):
        lc = self.agents - self.allocation[:, item].sum() - 1
        return lc

    # def add_item_source(self, source):

    def eliminate_cycle(self, cycle):
        source = cycle[0][0]
        source_tmp = self.allocation[cycle[0][0]].copy()
        for t in cycle:
            target = self.allocation[t[1]]
            if t[1] == source:
                target = source_tmp
            self.allocation[t[0]] = target

    def node2source(self, node):
        for s in self.source_nodes():
            if nx.has_path(self.nx_graph, s, node):
                return s

    def smallest_envy_set(self, t):
        n1, n2 = t
        v = self.valuation(n1, self.allocation[n2])
        self_v = sum(self.valuation(n1))
        other_v = sum(v)
        nv = v[np.nonzero(v)]
        nv = np.sort(nv)
        for i in range(len(nv)):
            other_v -= nv[i]
            if self_v >= other_v:
                return i

    def champion_set(self, agent, bundle):
        bundle = np.copy(bundle)
        while sum(self.valuation(agent)) < sum(self.valuation(agent, bundle=bundle)):
            v = self.valuation(agent, bundle=bundle)
            v_nz = v[np.nonzero(v)]
            m = np.min(v_nz)
            min_index = (np.where(v == m))[0][0]
            bundle[min_index] = 0
            if sum(self.valuation(agent)) > sum(self.valuation(agent, bundle=bundle)):
                bundle[min_index] = 1
                break
        if sum(self.valuation(agent)) < self.EFX_valuation(agent, bundle=bundle):
            print("EFX bug")
        return int(sum(bundle)), bundle

    def nash_welfare(self):
        nw = 0
        for i in range(self.agents):
            nw += self.valuation(i).sum()
        return nw

    def champion_of_bundle(self, envy_nodes, s, bundle):
        smallest_sets = [self.champion_set(envy_nodes[k], bundle) for k in
                         range(len(envy_nodes))]
        ss = [t[0] for t in smallest_sets]
        champion_index = np.argmin(np.array(ss))
        champion_node = envy_nodes[champion_index]
        champion_set = smallest_sets[champion_index][1]
        return champion_node, champion_set

    def remaining_coupons_array(self):
        r = np.zeros(self.items)
        for i in range(self.items):
            r[i] = self.remaining_coupon(i)
        return r
