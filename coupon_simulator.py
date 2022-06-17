# import numpy as np
# import random
#
#
# class CouponProblem:
#     agents = 1
#     items = 1
#     valuation_matrix = None
#     allocation = None
#     envy_graph = None
#
#     def __init__(self, agents, items):
#         self.agents = agents
#         self.items = items
#         self.valuation_matrix = np.zeros((agents, items))
#         for i in range(agents):
#             for j in range(items):
#                 self.valuation_matrix[i][j] = random.random()
#             self.valuation_matrix[i] = np.divide(self.valuation_matrix[i], sum(self.valuation_matrix[i]))
