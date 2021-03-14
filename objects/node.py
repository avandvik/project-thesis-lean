class Node:

    def __init__(self, index, is_order, order, installation, is_start_depot=False):
        self.index = index
        self._is_order = is_order
        self._is_depot = not is_order
        self._is_start_depot = is_start_depot
        self._is_end_depot = not is_start_depot and self._is_depot
        self.order = order if is_order else None
        self.installation = installation

    def is_order(self):
        return self._is_order

    def is_depot(self):
        return self._is_depot

    def is_start_depot(self):
        return self._is_depot and self._is_start_depot

    def is_end_depot(self):
        return self._is_depot and self._is_end_depot

    def get_order(self):
        return self.order

    def get_installation(self):
        return self.installation

    def get_index(self):
        return self.index

    def generate_representation(self):
        return f'{"Depot" if not self.is_order() else self.order}'

    def __str__(self):
        return self.generate_representation()

    def __repr__(self):
        return self.generate_representation()
