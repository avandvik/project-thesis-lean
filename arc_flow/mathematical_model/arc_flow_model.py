import time
import gurobipy as gp

import data
from arc_flow.preprocessing.arc_generator import ArcGenerator
from arc_flow.preprocessing.penalty_cost_calculator import calculate_penalty_costs
import arc_flow.mathematical_model.variable_generator as vg
import arc_flow.mathematical_model.constraint_generator as cg
import arc_flow.postprocessing as post


class ArcFlowModel:

    def __init__(self):
        with gp.Env(data.LOG_OUTPUT_PATH, empty=True) as env:
            env.setParam('LogToConsole', 1)
            env.start()
            self.model = gp.Model(name=data.LOG_OUTPUT_PATH, env=env)

        self.model.setParam('TimeLimit', data.TIME_LIMIT)

        self.ag = ArcGenerator(data.VERBOSE)
        self.nodes = None
        self.arcs = None
        self.arc_costs = None
        self.sep_arc_costs = None
        self.arc_arrival_times = None
        self.arc_speeds = None
        self.penalty_costs = None

        self.node_time_points = None
        self.start_nodes = None
        self.end_nodes = None
        self.start_times = None
        self.end_times = None
        self.specific_start_times = None
        self.specific_end_times = None

        self.x = {}
        self.u = {}
        self.l_D = {}
        self.l_P = {}

    def preprocess(self):
        self.ag.generate_arcs()
        self.arcs = self.ag.get_arcs()
        self.arc_costs = self.ag.get_arc_costs()
        self.sep_arc_costs = self.ag.get_sep_arc_costs()
        self.arc_arrival_times = self.ag.get_arc_arrival_times()
        self.arc_speeds = self.ag.get_arc_speeds()
        self.penalty_costs = calculate_penalty_costs(self.arcs, self.arc_costs)

        self.node_time_points = self.ag.get_node_time_points()
        self.start_nodes = self.ag.get_start_nodes()
        self.end_nodes = self.ag.get_end_nodes()
        self.start_times = self.ag.get_start_times()
        self.end_times = self.ag.get_end_times()
        self.specific_start_times = self.ag.get_specific_start_times()
        self.specific_end_times = self.ag.get_specific_end_times()

    def add_variables(self):
        self.x = vg.initialize_arc_variables(self.model, self.start_times, self.specific_end_times)
        self.u = vg.initialize_order_served_variables(self.model)
        self.l_D = vg.initialize_delivery_load_variables(self.model)
        self.l_P = vg.initialize_pickup_load_variables(self.model)
        self.model.update()

    def add_constraints(self):
        cg.add_flow_conservation_constrs(self.model, self.x, self.start_nodes, self.end_nodes,
                                         self.specific_start_times, self.specific_end_times,
                                         self.node_time_points)
        cg.add_start_and_end_flow_constrs(self.model, self.x, self.start_times, self.specific_end_times)
        cg.add_visit_limit_constrs(self.model, self.x, self.u, self.start_times, self.specific_end_times)
        cg.add_initial_delivery_load_constrs(self.model, self.l_D, self.l_P, self.u)
        cg.add_load_capacity_constrs(self.model, self.l_D, self.l_P, self.u)
        cg.add_load_continuity_constrs_1(self.model, self.x, self.l_D, self.l_P, self.u, self.start_times,
                                         self.specific_end_times)
        cg.add_load_continuity_constrs_2(self.model, self.x, self.l_D, self.l_P, self.start_times,
                                         self.specific_end_times)
        cg.add_final_pickup_load_constrs(self.model, self.l_P, self.u)
        self.model.update()

    def set_objective(self):
        self.model.setObjective(gp.quicksum(self.arc_costs[v][i][t1][j][t2] * self.x[v, i, t1, j, t2]
                                            for v in range(len(data.VESSELS))
                                            for i in range(len(data.ALL_NODES))
                                            for j in range(len(data.ALL_NODES)) if i != j
                                            for t1 in self.start_times[v][i][j]
                                            for t2 in self.specific_end_times[v][i][j][t1])

                                +

                                gp.quicksum(self.penalty_costs[i] * (1 - gp.quicksum(self.u[v, i]
                                                                                     for v in range(len(data.VESSELS))))
                                            for i in data.ALL_NODE_INDICES)

                                +

                                gp.quicksum(self.l_D[v, i] + self.l_P[v, i]
                                            for v in range(len(data.VESSELS))
                                            for i in data.ALL_NODE_INDICES)

                                , gp.GRB.MINIMIZE)

        self.model.update()

    def run(self):
        preprocess_start = time.time()
        self.preprocess()
        preprocess_runtime = round(time.time() - preprocess_start, 4)

        self.add_variables()
        self.add_constraints()
        self.set_objective()

        if data.VERBOSE:
            self.model.printStats()

        self.model.optimize()
        model_runtime = round(self.model.Runtime, 4)

        voyages = post.create_voyages_variable(self.model.getVars(), self.arc_arrival_times, self.arc_speeds,
                                               self.sep_arc_costs)
        postponed_orders, serviced_orders = post.find_postponed_orders(voyages)
        fleet_vessels, chartered_vessels = post.find_vessels_used(voyages)
        bound, fuel_costs, charter_costs, arc_costs, penalty_costs = post.separate_objective(self.model.objVal,
                                                                                             self.model.objBound,
                                                                                             self.model.getVars(),
                                                                                             self.arc_costs, voyages)
        optimality_gap = self.model.MIPGap
        number_of_variables = self.model.NumVars
        number_of_bin_variables = self.model.NumBinVars
        number_of_cont_variables = number_of_variables - number_of_bin_variables

        if data.VERBOSE:
            post.print_nodes_and_orders()
            self.model.printAttr('X')
            print(f'Fuel costs: {fuel_costs}')
            print(f'Charter costs: {charter_costs}')
            print(f'Arc costs: {arc_costs}')
            print(f'Penalty costs: {self.penalty_costs}')
            print(f'Postponed orders: {postponed_orders}')
            print(f'Charter costs: {charter_costs}')

        post.save_results(voyages=voyages,
                          postponed_orders=postponed_orders,
                          serviced_orders=serviced_orders,
                          fleet_vessels=fleet_vessels,
                          chartered_vessels=chartered_vessels,
                          preprocess_runtime=preprocess_runtime,
                          model_runtime=model_runtime,
                          fuel_costs=fuel_costs,
                          charter_costs=charter_costs,
                          penalty_costs=penalty_costs,
                          objective_bound=bound,
                          optimality_gap=optimality_gap,
                          number_of_variables=number_of_variables,
                          number_of_bin_variables=number_of_bin_variables,
                          number_of_arcs=self.ag.get_number_of_arcs(),
                          number_of_cont_variables=number_of_cont_variables,
                          output_path=data.RESULTS_OUTPUT_PATH)


if __name__ == '__main__':
    afm = ArcFlowModel()
    afm.run()
