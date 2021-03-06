class Order:

    def __init__(self, index, transport_type, mandatory, size, installation_id):
        self.index = index
        self.transport_type = transport_type
        self.mandatory = mandatory
        self.size = size
        self.installation_id = installation_id

    def is_mandatory(self):
        return self.mandatory

    def is_optional(self):
        return not self.mandatory

    def is_delivery(self):
        return self.transport_type == 'delivery'

    def is_pickup(self):
        return self.transport_type == 'pickup'

    def is_mandatory_delivery(self):
        return self.mandatory and self.transport_type == 'delivery'

    def is_optional_delivery(self):
        return not self.mandatory and self.transport_type == 'delivery'

    def is_optional_pickup(self):
        return not self.mandatory and self.transport_type == 'pickup'

    def get_index(self):
        return self.index

    def get_size(self):
        return self.size

    def get_installation_id(self):
        return self.installation_id

    def generate_representation(self):
        return f'(O{self.index}-{"M" if self.is_mandatory() else "O"}{"D" if self.is_delivery() else "P"}' \
               f'-I{self.installation_id})'

    def __repr__(self):
        return self.generate_representation()

    def __str__(self):
        return self.generate_representation()
