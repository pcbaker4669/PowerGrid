class PowerPlant:
    def __init__(self, name, capacity, capital_cost, operating_cost, cost_per_mw):
        self.name = name
        self.capacity = capacity
        self.generated = 0
        self.capital_cost = capital_cost
        self.operating_cost = operating_cost
        self.cost_per_mw = cost_per_mw

    def __str__(self):
        return ("Plant: {}, capacity: {}, generated: {}".
                format(self.name, self.capacity, self.generated))


class Substation:
    def __init__(self, name, capacity, capital_cost, operating_cost):
        self.name = name
        self.capacity = capacity
        self.load = 0
        self.capital_cost = capital_cost
        self.operating_cost = operating_cost

    def __str__(self):
        return ("Sub: {}, capacity: {}, load: {}".
                format(self.name, self.capacity, self.load))


class Consumer:
    def __init__(self, name, demand, rate_per_mwh):
        self.name = name
        self.demand = demand
        self.received = 0
        self.rate_per_mwh = rate_per_mwh
        self.payment = 0

    def calculate_payment(self):
        self.payment = self.received * self.rate_per_mwh

    def __str__(self):
        return ("Name: {}, Demand: {}, Received: {}"
                .format(self.name, self.demand, self.received))

