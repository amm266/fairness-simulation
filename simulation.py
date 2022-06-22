import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

draw_of = False


def to_end(arr: list, item):
    arr.remove(item)
    arr.append(item)
    return arr


def to_front(arr: list, item):
    arr.remove(item)
    arr = [item] + arr
    return arr


def value2index(vec, value):
    for i in range(len(vec)):
        if vec[i] == value:
            return i


def draw_graph(p, title="", erase=True, stop=True):
    p.create_envy_graph()
    if not draw_of:
        # if erase:
        #     plt.clf()
        # if create_graph:
        if p.envy_graph is None:
            p.create_envy_graph()
        g = p.nx_graph
        if p.nx_graph_pos is None:
            p.nx_graph_pos = nx.spring_layout(g)
        pos = p.nx_graph_pos
        ax = plt.gca()
        ax.set_title(title)
        for envy_val, color in zip((1, 2), ("blue", "red")):
            edges = [(u, v) for u, v, d in g.edges.data(data='weight') if d == envy_val]
            nx.draw_networkx_edges(g, pos=pos, edgelist=edges, edge_color=color, ax=ax)
        nx.draw_networkx_labels(g, pos=pos, ax=ax)
        nx.draw_networkx_nodes(g, pos=pos, ax=ax)
        plt.show(title="end")
        # if stop:
        #     input()


class ChoreProblem:
    agents = 1
    items = 1
    valuation_matrix = None
    allocation = None
    envy_graph = None
    nx_graph = None
    nx_graph_pos = None
    self_allocation_delusion = dict()
    other_allocation_delusion = dict()
    order = None

    def __init__(self, agents, items, valuation=None):
        self.agents = agents
        self.items = items
        self.allocation = np.zeros((agents, items))
        self.order = [i for i in range(items)]
        if valuation is None:
            self.valuation_matrix = np.zeros((agents, items))
            for i in range(agents):
                for j in range(items):
                    self.valuation_matrix[i][j] = round(random.random(), 2)
                self.valuation_matrix[i] = np.divide(self.valuation_matrix[i], sum(self.valuation_matrix[i]))
        else:
            self.valuation_matrix = np.array(valuation)

    def late_order(self, item):
        self.order.remove(item)
        self.order.append(item)

    def get_bundle(self, agent, for_agent=None):
        if for_agent is None or for_agent not in self.other_allocation_delusion:
            if agent in self.self_allocation_delusion:
                return self.self_allocation_delusion[agent]
            return self.allocation[agent]
        return self.other_allocation_delusion[for_agent][agent]

    def nash_allocation(self):
        allocation = np.zeros((self.agents, self.items))
        for i in range(self.items):
            index = np.argmin(self.valuation_matrix[:, i])
            allocation[index, i] = 1
        self.allocation = allocation
        return allocation

    def valuation(self, agent, bundle=None, for_node=None):
        if bundle is None:
            bundle = self.get_bundle(agent, for_agent=for_node)
        v = np.zeros(self.items)
        for i in range(self.items):
            v[i] = bundle[i] * self.valuation_matrix[agent, i]
        return v

    def EFX_valuation(self, agent, bundle=None):
        if bundle is None:
            bundle = self.get_bundle(agent)
        bundle_ones = np.where(bundle == 1)
        v = self.valuation(agent, bundle)
        v_ones = v[bundle_ones]
        try:
            m = np.min(v_ones)
        except:
            m = 0
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
            if round(efx_other, 3) > self_v:
                r.append(i)
        r = np.array(r)
        return r


class CouponProblem(ChoreProblem):
    def examine(self):
        self.reset_old_allocation()
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
        return sum([self.remaining_coupon(i) for i in range(self.items)]) + sum(
            [self.agents - 1 for j in range(self.items) if self.remaining_coupon(j) < 0])

    def add_self_old_allocation(self, agent, bundle):
        if agent not in self.self_allocation_delusion:
            self.self_allocation_delusion[agent] = np.copy(bundle)

    def add_other_old_allocation(self, agent, allocation):
        self.other_allocation_delusion[agent] = allocation

    def reset_old_allocation(self):
        self.self_allocation_delusion = dict()
        self.other_allocation_delusion = dict()

    def create_envy_graph(self, zero_envy=False):
        self.envy_graph = np.zeros((self.agents, self.agents))
        for i in range(self.agents):
            bundle = self.get_bundle(i)
            for j in range(self.agents):
                if i == j:
                    continue
                self_v = sum(self.valuation(i, bundle=bundle))
                other_v = sum(self.valuation(i, bundle=self.allocation[j]))
                envy = self_v < other_v
                if zero_envy:
                    envy = self_v <= other_v
                if envy:
                    self.envy_graph[i][j] = 1
                    efx_other_v = self.EFX_valuation(i, bundle=self.allocation[j])
                    if self_v < round(efx_other_v, 3):
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
        main_bundle = np.copy(bundle)
        bundle = np.copy(bundle)
        while sum(self.valuation(agent)) < sum(self.valuation(agent, bundle=bundle)):
            bundle_ones = np.where(bundle == 1)
            v = self.valuation(agent, bundle=bundle)
            v_ones = v[bundle_ones]
            m = np.argmin(v_ones)
            bo = list(bundle_ones)[0]
            del_index = bo[m]
            bundle[del_index] = 0
            if sum(self.valuation(agent)) >= sum(self.valuation(agent, bundle=bundle)):
                bundle[del_index] = 1
                break
        # if sum(self.valuation(agent)) < self.EFX_valuation(agent, bundle=bundle):
        #     print("EFX bug")
        #     self.champion_set(agent, main_bundle)
        return int(sum(bundle)), bundle, agent

    def social_welfare(self):
        nw = 0
        for i in range(self.agents):
            nw += self.valuation(i, bundle=self.allocation[i, :]).sum()
        return nw

    def champion_of_bundle(self, envy_nodes, s, bundle):
        smallest_sets = [self.champion_set(k, bundle) for k in envy_nodes]
        ss = [t[0] for t in smallest_sets]
        champion_index = np.argmin(ss)
        champion_node = smallest_sets[champion_index][2]
        champion_set = smallest_sets[champion_index][1]
        return champion_node, champion_set

    def remaining_coupons_array(self):
        r = np.zeros(self.items)
        for i in range(self.items):
            r[i] = self.remaining_coupon(i)
        return r
