import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def value2index(vec, value):
    for i in range(len(vec)):
        if vec[i] == value:
            return i


def draw_graph(g):
    pos = nx.spring_layout(g)
    for envy_val, color in zip((1, 2), ("blue", "red")):
        edges = [(u, v) for u, v, d in g.edges.data(data='weight') if d == envy_val]
        nx.draw_networkx_edges(g, pos=pos, edgelist=edges, edge_color=color)
    nx.draw_networkx_nodes(g, pos=pos)
    nx.draw_networkx_labels(g, pos=pos)
    plt.show()


class Problem:
    agents = 1
    items = 1
    valuation_matrix = None
    allocation = None
    envy_graph = None

    def __init__(self, agents, items):
        self.agents = agents
        self.items = items
        self.valuation_matrix = np.zeros((agents, items))
        for i in range(agents):
            for j in range(items):
                self.valuation_matrix[i][j] = random.random()
            self.valuation_matrix[i] = np.divide(self.valuation_matrix[i], sum(self.valuation_matrix[i]))

    def nash_allocation(self):
        allocation = np.zeros((self.agents, self.items))
        for i in range(self.items):
            index = np.argmin(self.valuation_matrix[:, i])
            allocation[index, i] = 1
        self.allocation = allocation
        return allocation

    def valuation(self, agent, bundle=None):
        if bundle is None:
            bundle = self.allocation[agent]
        v = np.zeros(self.items)
        for i in range(self.items):
            v[i] = bundle[i] * self.valuation_matrix[agent, i]
        return v

    def EFX_valuation(self, agent, bundle=None):
        v = self.valuation(agent, bundle)
        return sum(v) - np.min(v[np.nonzero(v)])

    def EF_evaluate(self, a=1):
        for i in range(self.agents):
            self_v = sum(self.valuation(i))
            for j in range(self.agents):
                if i == j:
                    continue
                v = sum(self.valuation(i, self.allocation[j]))
                if self_v > a * v:
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
        g = nx.from_numpy_matrix(self.envy_graph, create_using=nx.DiGraph)
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


p = Problem(3, 5)
p.nash_allocation()
# p.nash_allocation()
# while not p.EFX_evaluate():
#     print(p.allocation)
#     tmp_allocation = p.allocation
#     p.sell_cheapest()
#     if np.array_equal(tmp_allocation, p.allocation):
#         print("bug ", p.valuation_matrix)
# print(p.allocation)
# print("done")
for i in range(1):
    p = Problem(3, 6)
    # print(p.valuation_matrix)
    # print("nash allocation: ", p.nash_allocation())
    # print("is EF: ", p.EF_evaluate())
    # is_efx = p.EFX_evaluate()
    # print("is EFX: ", is_efx)
    # print("envy graph: ", p.create_envy_graph())
    p.nash_allocation()
    draw_graph(p.create_envy_graph())
    plt.show()
    # while not p.EFX_evaluate():
    #     print(p.allocation)
    #     tmp_allocation = p.allocation
    #     p.sell_cheapest()
    #     if np.equal(tmp_allocation.all(), p.allocation.all()):
    #         print("bug ",p.valuation_matrix )
    print(p.allocation)
    print("envy graph:\n", p.envy_graph)
    print("done")
