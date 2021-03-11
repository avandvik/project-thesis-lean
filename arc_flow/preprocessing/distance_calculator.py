import math


def distance(inst_one, inst_two, unit):
    lat1 = inst_one.get_latitude()
    lat2 = inst_two.get_latitude()
    lon1 = inst_one.get_longitude()
    lon2 = inst_two.get_longitude()

    if lat1 == lat2 and lon1 == lon2:
        return 0

    theta = lon1 - lon2
    dist = math.sin(math.radians(lat1)) * math.sin(math.radians(lat2)) \
           + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(theta))

    dist = math.acos(dist)
    dist = math.degrees(dist)
    dist = dist * 60 * 1.1515
    if unit == 'K':
        dist = dist * 1.609344
    elif unit == 'N':
        dist = dist * 0.8684

    return dist
