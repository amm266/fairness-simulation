from simulation import *
from algorithm4 import *

simulation.draw_of = True
reversed_p = 0
for n in range(10000):
    p = CouponProblem(4, 20)
    r, p = coupon_allocation(p, debug=False)
    print("n is:", n)
    print("pool size: ", p.pool_size())
    if not p.examine():
        reversed_p += 1
        print("fauuuuuult")
        print(p.allocation)
        print("pool size: ", p.pool_size())
        g = p.create_envy_graph()
        print(p.envy_graph)
        draw_graph(p)
        print(p.EFX_evaluate())
        print(p.valuation_matrix)
        v2 = np.zeros_like(p.valuation_matrix)
        for i in range(p.items):
            v2[:, i] = p.valuation_matrix[:, p.items - 1 - i]
        p2 = CouponProblem(p.agents, p.items)
        p2.valuation_matrix = v2
        r2, p2 = coupon_allocation(p2, debug=False)
        if not p2.examine():
            print("reverse fault")
            break
        else:
            print("solved")
            print(p2.allocation)
            print("pool size: ", p2.pool_size())
            g = p2.create_envy_graph()
            print(p2.envy_graph)
            draw_graph(p2)
            print(p2.EFX_evaluate())
            print(p2.valuation_matrix)
        break
print(reversed_p)
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
