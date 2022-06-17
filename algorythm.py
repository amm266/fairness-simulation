import networkx as nx
import numpy as np

from simulation import *

main_sources = set()


def coupon_allocation(p: CouponProblem, debug=False):
    global main_sources
    nash_set = {-1}
    stoped = False
    while not stoped:
        p.reset_old_allocation()
        print("remaining: ", p.remaining_coupons_array())
        print_nash(nash_set, p, "R1 nash: ")
        print("befoar r1: ", p.allocation)
        # Rule #1
        nw1 = p.nash_welfare()
        r1(p)
        try:
            while True:
                r1(p)
                p.create_envy_graph()
                cycle = nx.find_cycle(p.nx_graph)
                p.eliminate_cycle(cycle)
        except:
            pass
        # Rule 2
        remaining_array = p.remaining_coupons_array()
        if p.pool_size() < p.agents:
            # allocation successfully
            return True
        if debug:
            draw_graph(p)
            print_nash(nash_set, p, "R2 nash: ")
            print("pool starting R2: ", p.pool_size())
            print("remaining: ", p.remaining_coupons_array())
        # print("remaining: ", p.remaining_coupons_array())
        old_allocation = np.copy(p.allocation)
        edited_sources = set()
        sources = p.source_nodes()
        for s in sources:
            stoped = True
            if debug:
                draw_graph(p)
                print(p.allocation)
            is_envy, champion_node = make_source_envied(p, s, remaining_array)
            if debug:
                print(p.allocation)
                draw_graph(p, create_graph=False)
            stoped = is_envy
            self_champ = champion_node == s
            if is_envy and not self_champ:
                edited_sources.add(s)
                if debug:
                    nw = p.nash_welfare()
                    draw_graph(p, create_graph=False)
                    print(p.allocation)
                success = find_eliminate_cycle(p, edited_sources, old_allocation)
                if debug:
                    print(p.allocation)
                    draw_graph(p)
                number_of_added = 1
                # while not success and not p.EFX_evaluate():
                while not success:
                    if debug:
                        draw_graph(p)
                        print(s, " ", champion_node)
                    number_of_added += 1
                    s = p.node2source(champion_node)
                    # if r1(p):
                    #     print("bug")
                    is_envy, champion_node = make_source_envied(p, s, remaining_array)
                    if champion_node == s:
                        self_champ = True
                        break
                    if debug:
                        draw_graph(p)
                    if not is_envy:
                        print("bbuugg", p.pool_size(), " ", number_of_added)
                        print("cannot make source not source: ", sources)
                        # is_envy, champion_node = make_source_envied(p, s)
                        return False
                    success = find_eliminate_cycle(p, edited_sources, old_allocation)
                stoped = False
                if debug:
                    nw2 = p.nash_welfare()
                    p.reset_old_allocation()
                    p.create_envy_graph()
                    if nw2 < nw1:
                        print("dec")
                    if not p.EFX_evaluate():
                        print("fosh")
                    print(p.allocation)
                    draw_graph(p)
                break
            if self_champ:
                stoped = False
                break
    print("stopped: ", stoped)
    p.create_envy_graph()
    draw_graph(p)
    print("cannot make source not source: ", sources)


def print_nash(nash_set, p, message):
    nw = p.nash_welfare()
    print(message, nw)
    if nw <= max(nash_set):
        print("repeat")
        print("val")
        print(p.valuation_matrix)
    nash_set.add(nw)


def r1(p):
    while safely_add_item(p):
        pass


def safely_add_item(p):
    for a in range(p.agents):
        for t in range(p.items):
            if p.allocation[a][t] != 1 and p.remaining_coupon(t) > 0:
                p.allocation[a][t] = 1
                p.create_envy_graph()
                l = np.where(p.envy_graph == 2)
                real = (len(l[0]) == 0)
                if real is True:
                    return True
                else:
                    p.allocation[a][t] = 0
    return False


def make_source_envied(p: coupon_allocation, s, remaining_array):
    global main_sources
    if sum(remaining_array) == 0:
        return False, None
    for coupon in np.nonzero(remaining_array)[0]:
        print("remaining: ", remaining_array)
        if p.allocation[s][coupon] == 0:
            print("allocating item ", coupon, " to agent: ", s)
            old_source = np.copy(p.allocation[s])
            p.add_old_allocation(s, old_source)
            p.allocation[s][coupon] = 1
            remaining_array[coupon] -= 1
            str_envying_nodes = p.strong_envy_nodes(s)
            if len(str_envying_nodes) == 0:
                print("bug")
                continue
            else:
                bundle = p.allocation[s].copy()
                p.allocation[s] = old_source
                str_envying_nodes = np.append(str_envying_nodes, s)
                champion_node, champion_set = p.champion_of_bundle(str_envying_nodes, s, bundle)
                # if p.valuation(0,)
                p.allocation[s] = champion_set
                p.create_envy_graph()
                return True, champion_node
    return False, None


def find_eliminate_cycle(p, edited_sources, old_allocation):
    r = False
    try:
        while True:
            # p.create_envy_graph()
            cycle = nx.find_cycle(p.nx_graph)
            print("remaining: ", p.remaining_coupons_array())
            print("cycle: ", cycle)
            cycle_nodes = [n[0] for n in cycle]
            for s in p.old_allocation:
                if s not in cycle_nodes:
                    p.allocation[s] = p.old_allocation[s]
            p.eliminate_cycle(cycle)
            p.create_envy_graph()
            print("remaining: ", p.remaining_coupons_array())

            # print("nash welfare cycle eliminated: ", p.nash_welfare())
            r = True
            break
        return r
    except:
        return r
