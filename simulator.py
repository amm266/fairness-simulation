import itertools
import json
# import Image

import numpy as np

from algorithm3 import *

simulation.draw_of = True
reversed_p = 0




for n in range(10000):
    print(n, " started")
    p = CouponProblem(3, 8)
    r = coupon_allocation(p, debug=False, late_order=False)
    print("pool size: ", p.pool_size())

    print(p.allocation)
    print(n, " ended")
    if not p.examine() or not r:
        reversed_p += 1
        print("fauuuuuult")
        print(p.allocation)
        print("pool size: ", p.pool_size())
        g = p.create_envy_graph()
        print(p.envy_graph)
        draw_graph(p)
        print(p.EFX_evaluate())
        j = ""
        print(json.dumps(p.valuation_matrix.tolist()))
        r = coupon_allocation(p, debug=False, late_order=True)
        if not p.examine() or not r:
            print("real fault")
        break


# v2 = np.zeros_like(p.valuation_matrix)
# for i in range(p.items):
#     v2[:, i] = p.valuation_matrix[:, p.items - 1 - i]
# p2 = CouponProblem(p.agents, p.items)
# p2.valuation_matrix = v2
# r2, p2 = coupon_allocation(p2, debug=False)
# if not p2.examine():
#     print("reverse fault")
#     break
# else:
#     print("solved")
#     print(p2.allocation)
#     print("pool size: ", p2.pool_size())
#     g = p2.create_envy_graph()
#     print(p2.envy_graph)
#     draw_graph(p2)
#     print(p2.EFX_evaluate())
#     print(p2.valuation_matrix)
# break
# print(reversed_p)


def all_agent_possible_val(items, parts, arr):
    r = []
    a = list(range(1, parts))
    if items == 1:
        arr.append(parts)
        return [arr]
    for i in a:
        arr_tmp = arr.copy()
        arr_tmp.append(i)
        r += (all_agent_possible_val(items - 1, parts - i, arr_tmp))
    return r


def all_possible_valuations(agents, items, parts):
    v = all_agent_possible_val(items, parts, [])
    return [list(valuation_matrix) for valuation_matrix in itertools.combinations_with_replacement(v, agents)]


def all_possible_valuations_problem(agents, items, parts):
    v = all_agent_possible_val(items, parts, [])
    n = 0
    for valuation_matrix in itertools.combinations_with_replacement(v, agents):
        valuation_matrix = np.array(valuation_matrix)
        c = valuation_matrix.sum(axis=0)
        if np.any(c == 0):
            continue
        else:
            n += 1
            print(n)
        # if n < 25400:
        #     continue
        print(n, " started")
        p = CouponProblem(agents, items, valuation=valuation_matrix)
        print(p.valuation_matrix)
        r = coupon_allocation(p, debug=False)
        print("pool size: ", p.pool_size())
        print(p.allocation)
        print(n, " ended")
        # n += 1
        if not p.examine() or not r:
            print("fauuuuuult")
            print(p.allocation)
            print("pool size: ", p.pool_size())
            g = p.create_envy_graph()
            print(p.envy_graph)
            draw_graph(p)
            print(p.EFX_evaluate())
            print(p.valuation_matrix)
            break

# all_possible_valuations_problem(3, 5, 10)
