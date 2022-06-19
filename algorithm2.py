import networkx as nx
import numpy as np

import simulation
from simulation import *

main_sources = set()


def coupon_allocation(p: CouponProblem, debug=False):
    global main_sources
    nash_set = {-1}
    stoped = False
    while not stoped:
        p.reset_old_allocation()
        if debug:
            print("remaining: ", p.remaining_coupons_array())
            print("before r1: ", p.allocation)
            print("val: ", p.valuation_matrix)
            draw_graph(p, title="before R1 " + str(p.nash_welfare()) + " " + str(p.pool_size()))
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
        if debug:
            print_nash(nash_set, p, "R2 nash: ")
            print("pool starting R2: ", p.pool_size())
            print("remaining: ", p.remaining_coupons_array())
            draw_graph(p, title="after R1 " + str(p.nash_welfare()) + " " + str(p.pool_size()))
        if p.pool_size() < p.agents:
            print("pool size: ",p.pool_size()," < agents: :",p.agents)
            # allocation successfully
            return True, p
        # print("remaining: ", p.remaining_coupons_array())
        old_allocation = np.copy(p.allocation)
        valuation = np.copy(p.valuation_matrix)
        edited_sources = set()
        sources = p.source_nodes()
        cycled = False
        while not cycled:
            p = CouponProblem(p.agents, p.items, valuation=p.valuation_matrix)
            p.allocation = np.copy(old_allocation)
            p.reset_old_allocation()
            remaining_array = p.remaining_coupons_array()

            is_added = False
            goto_while = False
            for s in sources:
                stoped = True
                if debug:
                    draw_graph(p,
                               title="add item to source " + str(s) + " " + str(p.nash_welfare()) + " " + str(
                                   p.pool_size()))
                    # print(p.allocation)
                is_envy, champion_node, is_del = make_source_envied(p, s, remaining_array)
                if is_del and is_added:
                    sources = to_front(sources, s)
                    break
                is_added = is_added or (not is_del)
                if debug:
                    # print(p.allocation)
                    draw_graph(p,
                               title="item added " + "champion: " + str(champion_node) + " " + str(s) + " " + str(
                                   p.nash_welfare()) + " " + str(
                                   p.pool_size()))
                stoped = not is_envy
                self_champ = champion_node == s
                if is_envy and not self_champ:
                    edited_sources.add(s)
                    if debug:
                        draw_graph(p, title="finding cycle " + str(p.nash_welfare()) + " " + str(p.pool_size()))
                    success = find_eliminate_cycle(p, edited_sources, old_allocation)
                    if debug:
                        draw_graph(p, title="cycle found:" + str(success) + " " + str(p.nash_welfare()) + " " + str(
                            p.pool_size()))
                    number_of_added = 1
                    # while not success and not p.EFX_evaluate():
                    while not success:
                        number_of_added += 1
                        s = p.node2source(champion_node)
                        if debug:
                            print(s, " ", champion_node)
                            draw_graph(p,
                                       title="add item to source " + str(s) + " " + str(p.nash_welfare()) + " " + str(
                                           p.pool_size()))
                        # if r1(p):
                        #     print("bug")
                        is_envy, champion_node, is_del = make_source_envied(p, s, remaining_array)
                        if is_del and is_added:
                            sources = to_front(sources, s)
                            goto_while = True
                            break
                        is_added = is_added or (not is_del)
                        if debug:
                            draw_graph(p,
                                       title="item added " + "champion: " + str(champion_node) + " " + str(s) + " " + str(
                                           p.nash_welfare()) + " " + str(
                                           p.pool_size()))
                        if champion_node == s:
                            self_champ = True
                            stoped = False
                            cycle_nodes = [s]
                            for sour in p.self_allocation_delusion:
                                if sour not in cycle_nodes:
                                    p.allocation[sour] = p.self_allocation_delusion[sour]
                            break

                        if not is_envy:
                            print("bbuugg", p.pool_size(), " ", number_of_added)
                            print("cannot make source not source: ", sources)
                            # is_envy, champion_node = make_source_envied(p, s)
                            return False
                        if debug:
                            draw_graph(p, title="finding cycle " + str(p.nash_welfare()) + " " + str(p.pool_size()))
                        success = find_eliminate_cycle(p, edited_sources, old_allocation)
                        if debug:
                            draw_graph(p, title="cycle found:" + str(success) + " " + str(p.nash_welfare()) + " " + str(
                                p.pool_size()))
                    # if np.equal(p.allocation.all(), old_allocation.all()):
                    #     continue
                    if goto_while:
                        break
                    cycled = True
                    break
                if self_champ:
                    stoped = False
                    cycled = True
                    break
        if debug:
            nw2 = p.nash_welfare()
            p.reset_old_allocation()
            p.create_envy_graph()
            if nw2 <= nw1:
                print("dec")
                # return False
            if not p.EFX_evaluate():
                print("EFX")
                # return False
            print(p.allocation)
            draw_graph(p, title="end of R2" + str(p.nash_welfare()) + " " + str(
                p.pool_size()))
    print("stopped: ", stoped)
    p.create_envy_graph()
    draw_graph(p)
    print("cannot make source not source: ", sources)


def print_nash(nash_set, p, message):
    nw = p.nash_welfare()
    print(message, nw)


def r1(p):
    while safely_add_item(p):
        pass


def safely_add_item(p):
    for a in range(p.agents):
        for t in p.order:
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
    for coupon in p.order:
        # print("remaining: ", remaining_array)
        if p.allocation[s][coupon] == 0 and coupon in np.nonzero(remaining_array)[0]:
            # print("allocating item ", coupon, " to agent: ", s)
            old_source = np.copy(p.allocation[s])
            p.add_self_old_allocation(s, old_source)
            p.allocation[s][coupon] = 1
            remaining_array[coupon] -= 1
            str_envying_nodes = set(p.strong_envy_nodes(s))
            if len(str_envying_nodes) == 0:
                print("bug")
                continue
            else:
                bundle = p.allocation[s].copy()
                # p.allocation[s] = old_source
                str_envying_nodes.add(s)
                champion_node, champion_set = p.champion_of_bundle(str_envying_nodes, s, bundle)
                # if p.valuation(0,)
                p.allocation[s] = champion_set
                p.create_envy_graph()
                return True, champion_node, False
    old_allocation = np.copy(p.allocation)
    p.add_other_old_allocation(s, old_allocation)
    del_indexes = find_del_indexes(p, s)
    while True:
        if len(del_indexes) == 0:
            break
        del_index = del_indexes.pop()
        print("del item: ", del_index)
        p.late_order(del_index)
        for i in range(p.agents):
            p.allocation[i][del_index] = 0

        str_envying_nodes = set(p.strong_envy_nodes(s))
        if len(str_envying_nodes) == 0:
            print("bug2")
            # continue
        else:
            bundle = p.allocation[s].copy()
            # p.allocation[s] = old_source
            str_envying_nodes.add(s)
            champion_node, champion_set = p.champion_of_bundle(str_envying_nodes, s, bundle)
            # if p.valuation(0,)
            p.allocation[s] = champion_set
            p.create_envy_graph()
            return True, champion_node, True
    return False, None, True


def find_eliminate_cycle(p, edited_sources, old_allocation):
    r = False
    try:
        while True:
            # p.create_envy_graph()
            cycle = nx.find_cycle(p.nx_graph)
            # print("remaining: ", p.remaining_coupons_array())
            # print("cycle: ", cycle)
            cycle_nodes = [n[0] for n in cycle]
            for s in p.self_allocation_delusion:
                if s not in cycle_nodes:
                    p.allocation[s] = p.self_allocation_delusion[s]
            p.eliminate_cycle(cycle)
            p.create_envy_graph()
            # print("remaining: ", p.remaining_coupons_array())

            # print("nash welfare cycle eliminated: ", p.nash_welfare())
            r = True
            break
        return r
    except:
        return r


def find_del_indexes(p, s):
    del_indexes = list(np.where(p.allocation[s] == 0)[0])
    no_s_alloc = np.copy(p.allocation)
    no_s_alloc = np.delete(no_s_alloc, s, axis=0)
    r = []
    for d in del_indexes:
        ar = no_s_alloc[:, d]
        x = np.all(ar == 0)
        if np.all(no_s_alloc[:, d] == 1):
            r.append(d)
    return r
