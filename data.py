import os
import json
import math
import pathlib

from objects.installation import Installation
from objects.vessel import Vessel
from objects.order import Order
from objects.node import Node

PROJECT_DIR_PATH = f'{pathlib.Path(__file__).parent.absolute()}'  # Path of the root of the project

LOCAL = False
if LOCAL:
    INSTANCE_NAME = 'example'
    INSTANCE_FILE_PATH = f'{PROJECT_DIR_PATH}/input/instance/{INSTANCE_NAME}.json'
    INSTALLATIONS_FILE_PATH = f'{PROJECT_DIR_PATH}/input/constant/installations.json'
    VESSELS_FILE_PATH = f'{PROJECT_DIR_PATH}/input/constant/vessels.json'
    WEATHER_FILE_PATH = f'{PROJECT_DIR_PATH}/input/constant/weather.json'
    LOG_OUTPUT_PATH = f'{PROJECT_DIR_PATH}/output/logs/{INSTANCE_NAME}.log'
    RESULTS_OUTPUT_PATH = f'{PROJECT_DIR_PATH}/output/results/{INSTANCE_NAME}.json'
else:
    INSTANCE_NAME = os.environ.get('instance_name')
    DIR_NAME = os.environ.get('dir_name')
    INPUT_FILE_PATH = f'{PROJECT_DIR_PATH}/input/{DIR_NAME}/{INSTANCE_NAME}.json'
    LOG_OUTPUT_PATH = f'/storage/users/anderhva/{os.environ.get("current_time")}/logs/{INSTANCE_NAME}.log'
    RESULTS_OUTPUT_PATH = f'/storage/users/anderhva/{os.environ.get("current_time")}/results/{INSTANCE_NAME}.json'

VERBOSE = True
SPEED_OPTIMIZATION = True
TIME_LIMIT = 60 * 60  # Max run time of gurobi solver

with open(INSTANCE_FILE_PATH) as file:
    instance_data = json.load(file)

with open(INSTALLATIONS_FILE_PATH) as file:
    installations_data = json.load(file)

with open(VESSELS_FILE_PATH) as file:
    vessels_data = json.load(file)

with open(WEATHER_FILE_PATH) as file:
    weather_data = json.load(file)

""" ============================ INSTALLATIONS ============================ """
INSTALLATIONS = []
for installation_name in installations_data:
    INSTALLATIONS.append(Installation(index=installations_data[installation_name]['id'],
                                      name=installation_name,
                                      opening_hour=installations_data[installation_name]['opening_hour'],
                                      closing_hour=installations_data[installation_name]['closing_hour'],
                                      latitude=installations_data[installation_name]['latitude'],
                                      longitude=installations_data[installation_name]['longitude']))

DEPOT = INSTALLATIONS[0]
UNIT_SERVICE_TIME_HOUR = vessels_data['real_service_time_per_unit']

""" ============================ VESSEL ============================ """
FUEL_PRICE = vessels_data['fuel_price']
SPOT_RATE = vessels_data['spot_hour_rate']
MIN_SPEED = vessels_data['min_speed']
MAX_SPEED = vessels_data['max_speed']
DESIGN_SPEED = vessels_data['design_speed']
FUEL_CONSUMPTION_DESIGN_SPEED = vessels_data['fc_design_speed']
FUEL_CONSUMPTION_DEPOT = vessels_data['fc_depot']
FUEL_CONSUMPTION_IDLING = vessels_data['fc_idling']
FUEL_CONSUMPTION_SERVICING = vessels_data['fc_servicing']
PREPARATION_END_HOUR = int(vessels_data['preparation_end_hour'])
SQM_IN_CARGO_UNIT = vessels_data['square_meters_in_one_cargo_unit']


VESSELS = []
index = 0
for vessel_name in vessels_data["fleet"]:
    is_spot_vessel = True if vessels_data["fleet"][vessel_name] == 'SPOT' else False
    if vessel_name in instance_data['available_vessels']:
        return_time = instance_data['available_vessels'][vessel_name]['return_time']
        VESSELS.append(Vessel(index=index,
                              name=vessel_name,
                              return_time=return_time,
                              capacity=vessels_data["fleet"][vessel_name]['capacity'] / SQM_IN_CARGO_UNIT,
                              is_spot_vessel=is_spot_vessel))
        index += 1

""" ============================ ORDERS ============================ """
ALL_NODES = []
ORDER_NODES = []

start_depot = Node(index=0, is_order=False, order=None, installation=DEPOT, is_start_depot=True)
ALL_NODES.append(start_depot)

for idx, order_id in enumerate(instance_data['orders']):
    installation_idx = instance_data['orders'][order_id]['installation']
    installation = INSTALLATIONS[installation_idx]

    order = Order(index=idx,
                  transport_type=instance_data['orders'][order_id]['transport'],
                  mandatory=True if instance_data['orders'][order_id]['mandatory'] == 'True' else False,
                  size=instance_data['orders'][order_id]['size'] / SQM_IN_CARGO_UNIT)

    node = Node(index=idx + 1, is_order=True, order=order, installation=installation)

    ORDER_NODES.append(order)
    ALL_NODES.append(node)
    installation.add_order(order)

end_depot = Node(index=len(ALL_NODES), is_order=False, order=None, installation=DEPOT, is_start_depot=False)
ALL_NODES.append(end_depot)

ALL_NODE_INDICES = [node.get_index() for node in ALL_NODES]
MANDATORY_NODE_INDICES = [node.get_index() for node in ALL_NODES if node.is_order() and node.get_order().is_mandatory()]
OPTIONAL_NODE_INDICES = [node.get_index() for node in ALL_NODES if node.is_order() and node.get_order().is_optional()]
DELIVERY_NODE_INDICES = [node.get_index() for node in ALL_NODES if node.is_order() and node.get_order().is_delivery()]
PICKUP_NODE_INDICES = [node.get_index() for node in ALL_NODES if node.is_order() and node.get_order().is_pickup()]

""" ============================ TIME AND DISCRETIZATION ============================ """
PERIOD_HOURS = int(instance_data['planning_period_hours'])
TIME_UNITS_PER_HOUR = int(instance_data['discretization_parameter'])
TIME_UNITS_24 = TIME_UNITS_PER_HOUR * 24
PERIOD_DISC = PERIOD_HOURS * TIME_UNITS_PER_HOUR
TIME_POINTS_DISC = [tp for tp in range(PERIOD_DISC)]

TIME_UNIT_DISC = 1.0 / TIME_UNITS_PER_HOUR
UNIT_SERVICE_TIME_DISC = UNIT_SERVICE_TIME_HOUR * TIME_UNITS_PER_HOUR

PREPARATION_END_TIME = PREPARATION_END_HOUR * TIME_UNITS_PER_HOUR - 1

""" ============================ WEATHER ============================ """
WEATHER_SCENARIO = instance_data['weather_scenario']
WEATHER_FORECAST_HOURS = weather_data['scenarios'][WEATHER_SCENARIO]
WEATHER_FORECAST_DISC = [WEATHER_FORECAST_HOURS[math.floor(i / TIME_UNITS_PER_HOUR)]
                         for i in range(len(WEATHER_FORECAST_HOURS) * TIME_UNITS_PER_HOUR)]
BEST_WEATHER_STATE = 0
WORST_WEATHER_STATE = weather_data['worst_weather_state']
SPEED_IMPACTS = [weather_data['speed_impact'][str(ws)] for ws in range(WORST_WEATHER_STATE + 1)]
SERVICE_IMPACTS = [weather_data['service_impact'][str(ws)] for ws in range(WORST_WEATHER_STATE + 1)]

""" ============================ INSTALLATION INFO ============================ """
INSTALLATION_ORDERING = instance_data['installation_ordering']
NUMBER_OF_INSTALLATIONS_WITH_ORDERS = len([inst for inst in INSTALLATIONS if len(inst.get_orders()) > 0])
FLEET_SIZE = len(VESSELS) - 1
