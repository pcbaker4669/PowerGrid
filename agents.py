class PowerPlant:
    def __init__(self, name, capacity, capital_cost, operating_cost, cost_per_mw):
        self.name = name
        self.capacity = capacity
        self.generated = 0
        self.capital_cost = capital_cost
        self.operating_cost = operating_cost
        self.cost_per_mw = cost_per_mw
        self.stepup_substations = []

    def connect_to_stepup(self, substation):
        self.stepup_substations.append(substation)

    def get_stepup_substations(self):
        return self.stepup_substations

    def __str__(self):
        return "Plant: {}, capacity: {}, generated: {}".format(self.name, self.capacity, self.generated)


class Substation:
    def __init__(self, name, capacity, capital_cost, operating_cost):
        self.name = name
        self.capacity = capacity
        self.load = 0
        self.capital_cost = capital_cost
        self.operating_cost = operating_cost

    def __str__(self):
        return "Sub: {}, capacity: {}, load: {}".format(self.name, self.capacity, self.load)


class StepUpSubstation(Substation):
    def __init__(self, name, capacity, capital_cost, operating_cost):
        super().__init__(name, capacity, capital_cost, operating_cost)
        self.stepdown_substations = []
        self.plants = []

    def connect_to_stepdown(self, substation):
        self.stepdown_substations.append(substation)

    def connect_to_plants(self, plant):
        self.plants.append(plant)

    def get_stepdowns(self):
        return self.stepdown_substations

    def get_plants(self):
        return self.plants


class StepDownSubstation(Substation):
    def __init__(self, name, capacity, capital_cost, operating_cost):
        super().__init__(name, capacity, capital_cost, operating_cost)
        self.stepup_substations = []
        self.customers = []

    def connect_to_stepup(self, substation):
        self.stepup_substations.append(substation)

    def connect_to_customers(self, customer):
        self.customers.append(customer)

    def get_stepups(self):
        return self.stepup_substations

    def get_customers(self):
        return self.customers


class Consumer:
    def __init__(self, name, demand, rate_per_mwh):
        self.name = name
        self.demand = demand
        self.received = 0
        self.rate_per_mwh = rate_per_mwh
        self.payment = 0
        self.stepdown_substations = []

    def connect_to_stepdown(self, substation):
        self.stepdown_substations = substation

    def calculate_payment(self):
        self.payment = self.received * self.rate_per_mwh

    def get_stepdowns(self):
        return self.stepdown_substations

    def __str__(self):
        return "Name: {}, Demand: {}, Received: {}".format(self.name, self.demand, self.received)