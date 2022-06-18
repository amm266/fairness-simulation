from simulation import *
from algorythm import *

p = CouponProblem(3, 10)
r = coupon_allocation(p, debug=True)
# print("n is:", n)
if not p.examine():
    print("fauuuuuult")
    print(p.allocation)
    print("pool size: ", p.pool_size())
    g = p.create_envy_graph()
    print(p.envy_graph)
    draw_graph(p)
    print(p.EFX_evaluate())
    print(p.valuation_matrix)
    # break

# print(p.allocation)
# print("pool size: ", p.pool_size())
# g = p.create_envy_graph()
# print(p.envy_graph)
# draw_graph(p)
# print(p.EFX_evaluate())
# print(p.valuation_matrix)
# try:
#     c = nx.find_cycle(g)
#     print(c)
# except:
#     pass
# print(p.EFX_evaluate())
# print(p.valuation_matrix)
# print(p.allocation)
# print(p.source_nodes())
# print(p.envy_graph)
