class Installation:

    def __init__(self, index, name, opening_hour, closing_hour, latitude, longitude):
        self.index = index
        self.name = name
        self.opening_hour = opening_hour
        self.closing_hour = closing_hour
        self.latitude = latitude
        self.longitude = longitude
        self.orders = []

    def add_order(self, order):
        self.orders.append(order)

    def has_multiple_orders(self):
        return len(self.orders) > 1

    def has_mandatory_order(self):
        for order in self.orders:
            if order.is_mandatory_delivery():
                return True
        return False

    def has_optional_delivery_order(self):
        for order in self.orders:
            if order.is_optional_delivery():
                return True
        return False

    def get_optional_orders(self):
        optional_orders = []
        for order in self.orders:
            if order.is_optional():
                optional_orders.append(order)
        return optional_orders

    def get_optional_pickup_order(self):
        for order in self.orders:
            if order.is_optional_pickup():
                return order

    def get_optional_delivery_order(self):
        for order in self.orders:
            if order.is_optional_delivery():
                return order

    def get_orders(self):
        return self.orders

    def get_most_dominating_order(self):
        if self.has_mandatory_order():
            for order in self.orders:
                if order.is_mandatory():
                    return order
        elif self.has_optional_delivery_order():
            for order in self.orders:
                if order.is_optional_delivery():
                    return order
        else:
            return self.orders[0]

    def get_opening_hours_as_list(self):
        return list(range(self.opening_hour, self.closing_hour + 1))

    def get_opening_and_closing_hours(self):
        return self.opening_hour, self.closing_hour

    def get_latitude(self):
        return self.latitude

    def get_longitude(self):
        return self.longitude

    def get_index(self):
        return self.index

    def get_name(self):
        return self.name

    def __repr__(self):
        return self.name
