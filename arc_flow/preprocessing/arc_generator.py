import data
import arc_flow.preprocessing.helpers as hlp
from collections import defaultdict as dd


class ArcGenerator:

    def __init__(self, verbose):
        # arcs[vessel][start_node][start_time][end_node][end_time] -> True/False
        self.arcs = dd(lambda: dd(lambda: dd(lambda: dd(lambda: dd(lambda: False)))))
        # arc_costs[vessel][start_node][start_time][end_node][end_time] -> arc_cost
        self.arc_costs = dd(lambda: dd(lambda: dd(lambda: dd(lambda: dd(lambda: 0)))))
        # sep_arc_costs[vessel][start_node][start_time][end_node][end_time] -> (fuel_cost, charter_cost)
        self.sep_arc_costs = dd(lambda: dd(lambda: dd(lambda: dd(lambda: dd(lambda: (0, 0))))))
        # arc_arrival_times[vessel][start_node][start_time][end_node][end_time] -> arrival_time
        self.arc_arrival_times = dd(lambda: dd(lambda: dd(lambda: dd(lambda: dd(lambda: 0)))))
        # arc_speeds[vessel][start_node][start_time][end_node][end_time] -> arc_speed
        self.arc_speeds = dd(lambda: dd(lambda: dd(lambda: dd(lambda: dd(lambda: 0)))))
        # node_time_points[vessel][node] -> time
        self.node_time_points = [[[] for _ in data.ALL_NODES] for _ in data.VESSELS]
        # start_nodes[vessel][end_node][end_time] -> start_node
        self.start_nodes = [[[[] for _ in data.TIME_POINTS_DISC] for _ in data.ALL_NODES] for _ in data.VESSELS]
        # end_nodes[vessel][start_node][start_time] -> end_node
        self.end_nodes = [[[[] for _ in data.TIME_POINTS_DISC] for _ in data.ALL_NODES] for _ in data.VESSELS]
        # start_times[vessel][start_node][end_node] -> start_time
        self.start_times = [[[[] for _ in data.ALL_NODES] for _ in data.ALL_NODES] for _ in data.VESSELS]
        # end_times[vessel][start_node][end_node] -> end_time
        self.end_times = [[[[] for _ in data.ALL_NODES] for _ in data.ALL_NODES] for _ in data.VESSELS]
        # specific_start_times[vessel][start_node][end_node][end_times] -> start_time
        self.specific_start_times = [[[[[] for _ in data.TIME_POINTS_DISC] for _ in data.ALL_NODES]
                                      for _ in data.ALL_NODES] for _ in data.VESSELS]
        # specific_end_times[vessel][start_node][end_node][start_time] -> end_time
        self.specific_end_times = [[[[[] for _ in data.TIME_POINTS_DISC] for _ in data.ALL_NODES]
                                    for _ in data.ALL_NODES] for _ in data.VESSELS]
        self.verbose = verbose
        self.number_of_arcs = 0

    def generate_arcs(self):
        for vessel in data.VESSELS:
            for start_node in data.ALL_NODES[:-1]:
                start_times = hlp.get_start_times(start_node, vessel)
                for end_node in data.ALL_NODES[1:]:
                    if hlp.is_illegal_arc(start_node, end_node):
                        continue
                    for start_time in start_times:
                        arr_times_to_arc_data, idling = hlp.get_arc_data(start_node, end_node, start_time, vessel)
                        if not arr_times_to_arc_data:
                            continue
                        self.save_arcs(start_node, end_node, start_time, arr_times_to_arc_data, vessel, idling)

    def save_arcs(self, start_node, end_node, start_time, arr_times_to_arc_data, vessel, idling):
        if end_node.is_end_depot() or idling:
            self.add_best_arc(start_node, end_node, start_time, arr_times_to_arc_data, vessel)
        else:
            self.add_arcs(start_node, end_node, start_time, arr_times_to_arc_data, vessel)

    def add_best_arc(self, start_node, end_node, start_time, arr_times_to_arc_data, vessel):
        best_arr_time, best_cost = 1E10, 1E10
        for arr_time in arr_times_to_arc_data:
            cost = arr_times_to_arc_data[arr_time][-1] + arr_times_to_arc_data[arr_time][-2]
            if cost < best_cost:
                best_arr_time, best_cost = arr_time, cost
        end_time, speed, fuel_cost, charter_cost = arr_times_to_arc_data[best_arr_time][1:]
        self.update_sets(start_node, end_node, fuel_cost, charter_cost, start_time, best_arr_time, end_time, speed,
                         vessel)

    def add_arcs(self, start_node, end_node, start_time, arr_times_to_arc_data, vessel):
        for arr_time in arr_times_to_arc_data:
            end_time, speed, fuel_cost, charter_cost = arr_times_to_arc_data[arr_time][1:]
            self.update_sets(start_node, end_node, fuel_cost, charter_cost, start_time, arr_time, end_time, speed,
                             vessel)

    def update_sets(self, sn, en, fc, cc, ast, aat, aet, s, v):
        self.arcs[v.get_index()][sn.get_index()][ast][en.get_index()][aet] = True
        self.arc_costs[v.get_index()][sn.get_index()][ast][en.get_index()][aet] = fc + cc
        self.sep_arc_costs[v.get_index()][sn.get_index()][ast][en.get_index()][aet] = (fc, cc)
        self.arc_arrival_times[v.get_index()][sn.get_index()][ast][en.get_index()][aet] = aat
        self.arc_speeds[v.get_index()][sn.get_index()][ast][en.get_index()][aet] = s
        self.number_of_arcs += 1

        if aet not in self.node_time_points[v.get_index()][en.get_index()]:
            self.node_time_points[v.get_index()][en.get_index()].append(aet)
        if sn.get_index() not in self.start_nodes[v.get_index()][en.get_index()][aet]:
            self.start_nodes[v.get_index()][en.get_index()][aet].append(sn.get_index())
        if en.get_index() not in self.end_nodes[v.get_index()][sn.get_index()][ast]:
            self.end_nodes[v.get_index()][sn.get_index()][ast].append(en.get_index())
        if ast not in self.start_times[v.get_index()][sn.get_index()][en.get_index()]:
            self.start_times[v.get_index()][sn.get_index()][en.get_index()].append(ast)
        if aet not in self.end_times[v.get_index()][sn.get_index()][en.get_index()]:
            self.end_times[v.get_index()][sn.get_index()][en.get_index()].append(aet)
        if ast not in self.specific_start_times[v.get_index()][sn.get_index()][en.get_index()][aet]:
            self.specific_start_times[v.get_index()][sn.get_index()][en.get_index()][aet].append(ast)
        if aet not in self.specific_end_times[v.get_index()][sn.get_index()][en.get_index()][ast]:
            self.specific_end_times[v.get_index()][sn.get_index()][en.get_index()][ast].append(aet)

    def print_arcs(self, start_from, start_to, end_from, end_to, v):
        print(f'Orders: {data.ALL_NODES}')
        counter = 0
        for start_node in data.ALL_NODES[start_from:start_to]:
            for end_node in data.ALL_NODES[end_from:end_to]:
                for start_time in range(data.PREPARATION_END_TIME, data.PERIOD_DISC):
                    for end_time in range(data.PREPARATION_END_TIME, data.PERIOD_DISC):
                        if self.arcs[v][start_node.get_index()][start_time][end_node.get_index()][end_time]:
                            arc_cost = self.arc_costs[v][start_node.get_index()][start_time][end_node.get_index()][
                                end_time]
                            arc_speed = self.arc_speeds[v][start_node.get_index()][start_time][end_node.get_index()][
                                end_time]
                            print(f'({start_node}, {start_time}) -> {end_node}, {end_time}): '
                                  f'{round(arc_cost, 4)} {arc_speed}')
                            counter += 1
        print(f'Number of arcs: {counter}')

    def get_arcs(self):
        return self.arcs

    def get_arc_costs(self):
        return self.arc_costs

    def get_sep_arc_costs(self):
        return self.sep_arc_costs

    def get_arc_arrival_times(self):
        return self.arc_arrival_times

    def get_arc_speeds(self):
        return self.arc_speeds

    def get_node_time_points(self):
        return self.node_time_points

    def get_start_nodes(self):
        return self.start_nodes

    def get_end_nodes(self):
        return self.end_nodes

    def get_start_times(self):
        return self.start_times

    def get_end_times(self):
        return self.end_times

    def get_specific_start_times(self):
        return self.specific_start_times

    def get_specific_end_times(self):
        return self.specific_end_times

    def get_number_of_arcs(self):
        return self.number_of_arcs


# ag = ArcGenerator(verbose=True)
# ag.generate_arcs()
# ag.print_arcs(0, len(data.ALL_NODES), 0, len(data.ALL_NODES), 0)  # Vessel 0
