class Vessel:

    def __init__(self, index, name, return_time, capacity, is_spot_vessel, fc_design_speed):
        self.index = index
        self.name = name
        self.return_time = return_time
        self.capacity = capacity
        self._is_spot_vessel = is_spot_vessel
        self.fc_design_speed = fc_design_speed

    def is_spot_vessel(self):
        return self._is_spot_vessel

    def get_hourly_return_time(self):
        return self.return_time

    def get_capacity(self):
        return self.capacity

    def get_index(self):
        return self.index

    def get_fc_design_speed(self):
        return self.fc_design_speed

    def __str__(self):
        return f'Vessel {self.name}'

    def __repr__(self):
        return f'Vessel {self.name}'
