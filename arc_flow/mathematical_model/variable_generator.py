import data
import gurobipy as gp


def initialize_arc_variables(model, departure_times, specific_arrival_times):
    x = {}

    for v in range(len(data.VESSELS)):
        for i in range(len(data.ALL_NODES)):
            for j in range(len(data.ALL_NODES)):
                if i == j:
                    continue
                for t1 in departure_times[v][i][j]:
                    for t2 in specific_arrival_times[v][i][j][t1]:
                        x[v, i, t1, j, t2] = model.addVar(vtype=gp.GRB.BINARY, name=f'x_{i}_{t1}_{j}_{t2}_{v}')

    return x


def initialize_order_served_variables(model):
    u = {}

    for v in range(len(data.VESSELS)):
        for i in range(len(data.ALL_NODES)):
            u[v, i] = model.addVar(vtype=gp.GRB.BINARY, name=f'u_{i}_{v}')

    return u


def initialize_delivery_load_variables(model):
    l_D = {}

    for v in range(len(data.VESSELS)):
        for i in range(len(data.ALL_NODES)):
            l_D[v, i] = model.addVar(vtype=gp.GRB.CONTINUOUS, name=f'l_D_{i}_{v}')

    return l_D


def initialize_pickup_load_variables(model):
    l_P = {}

    for v in range(len(data.VESSELS)):
        for i in range(len(data.ALL_NODES)):
            l_P[v, i] = model.addVar(vtype=gp.GRB.CONTINUOUS, name=f'l_P_{i}_{v}')

    return l_P
