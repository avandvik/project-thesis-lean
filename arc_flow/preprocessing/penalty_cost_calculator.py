import math

import data

import arc_flow.preprocessing.distance_calculator as dc
import arc_flow.preprocessing.helpers as hlp


def calculate_penalty_costs():
    penalty_costs = [0 for _ in data.ALL_NODE_INDICES]

    for order in data.ORDER_NODES:
        if not order.is_mandatory():
            installation = data.INSTALLATIONS[order.get_installation_id()]
            distance = dc.distance(data.DEPOT, installation, 'N')
            start_time = data.PREPARATION_END_TIME
            arr_time = start_time + math.floor(hlp.hour_to_disc(distance / data.DESIGN_SPEED))
            node = data.ALL_NODES[order.get_index() + 1]
            service_end_time = arr_time + hlp.calculate_service_time(node)
            sail_cost = hlp.calculate_fuel_cost_sailing(start_time, arr_time, data.DESIGN_SPEED, distance) * 2
            service_cost = hlp.calculate_fuel_cost_servicing(arr_time, service_end_time)
            penalty_costs[order.get_index() + 1] = sail_cost + service_cost

    return penalty_costs
