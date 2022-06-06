import random
import numpy as np

r = random.random()


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
        self.envy_graph = np.zeros_like(self.valuation_matrix)
        for i in range(self.agents):
            self_v = sum(self.valuation(i))
            for j in range(self.agents):
                if i == j:
                    continue
                v = sum(self.valuation(i, self.allocation[j]))
                if self_v > v:
                    self.envy_graph[i][j] = 1
        return self.envy_graph


p = Problem(5, 20)
print(p.valuation_matrix)
print("nash allocation: ", p.nash_allocation())
print("is EF: ", p.EF_evaluate())
print("is EFX: ", p.EFX_evaluate())
print("envy graph: ", p.create_envy_graph())
