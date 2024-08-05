import agents as ag
import networkx as nx
import random

# Set random seed for reproducibility (uncomment if needed)
random.seed(123456)


class Model:
    def __init__(self, num_plants=3, num_up_substations=2, num_dwn_substations=2, num_consumers=5,
                 extra_lines_req=0):
        self.G = nx.Graph()
        self.num_plants = num_plants
        self.num_up_substations = num_up_substations
        self.num_dwn_substations = num_dwn_substations
        self.num_consumers = num_consumers
        self.agents = {}
        self.extra_lines_req = extra_lines_req
        self.extra_lines_used = 0
        self.verbose = False
        self.pnt_to_su_cap = 50
        self.su_to_dn_cap = 250
        self.sd_to_customer_cap = 65

    # Step 1: Define the Grid Structure
    def create_grid(self):
        self.agents = {}
        plants_dict = {}
        su_subs_dict = {}
        sd_subs_dict = {}
        customers_dict = {}
        # Add power plants
        for i in range(self.num_plants):
            name = f'P{i}'
            capacity = random.randint(50, 100)
            plant = ag.PowerPlant(name, capacity, 1000000, 5000, 50)
            self.agents[name] = plant
            plants_dict[name] = plant  # local list for plants
            self.G.add_node(name, type='plant', capacity=capacity)

        # Add step-up substations with capacity
        for up_subs in range(self.num_up_substations):
            name = f'SU{up_subs}'
            capacity = random.randint(100, 200)
            su_sub = ag.StepUpSubstation(name, capacity, 1000000, 50000)
            self.agents[name] = su_sub
            su_subs_dict[name] = su_sub
            self.G.add_node(name, type='stepup', capacity=capacity)

        # Add step-down substations with capacity
        for dwn_subs in range(self.num_dwn_substations):
            name = f'SD{dwn_subs}'
            capacity = random.randint(100, 200)
            sd_sub = ag.StepDownSubstation(name, 'capacity', 1000000, 50000)
            self.agents[name] = sd_sub
            sd_subs_dict[name] = sd_sub
            self.G.add_node(name, type='stepdown', capacity=capacity)

        # Add consumers with demand
        for i in range(self.num_consumers):
            name = f'C{i}'
            demand = random.randint(5, 20)
            customer = ag.Consumer(name, demand, 100)
            self.agents[name] = customer
            customers_dict[name] = customer
            self.G.add_node(name, type='consumer', demand=demand)

        # Connect plants to setup substations
        # if more plants then substations, some plants will share substations
        # if more substations than plants (more likely), some substations will share
        # plants
        for su_sub_name, su_sub in su_subs_dict.items():
            plant_name = random.choice(list(plants_dict.keys()))
            plant_obj = plants_dict[plant_name]
            su_sub.connect_to_plants(plant_name)
            plant_obj.connect_to_stepup(su_sub_name)
            self.G.add_edge(plant_name, su_sub_name, capacity=50)

        # Ensure each power plant is connected to at least one step-up substation
        for plant_name, plant_obj in plants_dict.items():
            if len(plant_obj.get_stepup_substations()) == 0:
                su_sub_name = random.choice(list(su_subs_dict.keys()))
                su_sub_obj = su_subs_dict[su_sub_name]
                su_sub_obj.connect_to_plants(plant_name)
                plant_obj.connect_to_stepup(su_sub_name)
                self.G.add_edge(plant_name, su_sub_name, capacity=self.pnt_to_su_cap)

        # Ensure each step-up substation is connected to at least one step-down substation
        for su_sub_name, su_sub_obj in su_subs_dict.items():
            sd_sub_name = random.choice(list(sd_subs_dict.keys()))
            sd_sub_obj = sd_subs_dict[sd_sub_name]
            sd_sub_obj.connect_to_stepup(su_sub_name)
            su_sub_obj.connect_to_stepdown(sd_sub_name)
            self.G.add_edge(su_sub_name, sd_sub_name, capacity=self.su_to_dn_cap)

        # we are up to here...
        # Ensure each step-down substation is connected to at least one step-up substation
        for sd_sub_name, sd_sub_obj in sd_subs_dict.items():
            if len(sd_sub_obj.get_stepups()) == 0:
                su_sub_name = random.choice(list(su_subs_dict.keys()))
                su_sub_obj = su_subs_dict[su_sub_name]
                sd_sub_obj.connect_to_stepup(su_sub_name)
                su_sub_obj.connect_to_stepdown(sd_sub_name)
                self.G.add_edge(su_sub_name, sd_sub_name, capacity=self.su_to_dn_cap)

        # Ensure each customer is connected to at least one step-down substation
        for customer_name, customer_obj in customers_dict.items():
            sd_sub_name = random.choice(list(sd_subs_dict.keys()))
            sd_sub_obj = sd_subs_dict[sd_sub_name]
            customer_obj.connect_to_stepdown(sd_sub_name)
            sd_sub_obj.connect_to_customers(customer_name)
            self.G.add_edge(sd_sub_name, customer_name, capacity=self.sd_to_customer_cap)

        return self.G

    def initialize_agents(self):
        return self.agents

    def simulate_power_flow(self):
        # Reset generated and received power
        for node, agent in self.agents.items():
            if isinstance(agent, ag.PowerPlant):
                agent.generated = 0
            elif isinstance(agent, ag.Consumer):
                agent.received = 0
            elif isinstance(agent, ag.Substation):
                agent.load = 0

        # Distribute power from plants to substations
        for node in self.G.nodes():
            if self.G.nodes[node]['type'] == 'plant':
                plant = self.agents[node]
                print("plant ==> ", plant.name)
                for neighbor in self.G.neighbors(node):
                    if self.G.nodes[neighbor]['type'] == 'stepup':
                        substation = self.agents[neighbor]
                        capacity = self.G[node][neighbor]['capacity']
                        generated_power = min(plant.capacity - plant.generated, capacity)
                        plant.generated += generated_power
                        substation.load += generated_power
                        print("substation (su): {}, recieved: {}MW".
                              format(substation.name, substation.load))


            # Distribute power from step-up to step-down substations
        for node in self.G.nodes():
            if self.G.nodes[node]['type'] == 'stepup':
                substation = self.agents[node]
                for neighbor in self.G.neighbors(node):
                    if self.G.nodes[neighbor]['type'] == 'stepdown':
                        stepdown = self.agents[neighbor]
                        capacity = self.G[node][neighbor]['capacity']
                        transmitted_power = min(substation.load, capacity)
                        substation.load -= transmitted_power
                        stepdown.load += transmitted_power

        # Distribute power from step-down substations to consumers
        for node in self.G.nodes():
            if self.G.nodes[node]['type'] == 'stepdown':
                substation = self.agents[node]
                for neighbor in self.G.neighbors(node):
                    if self.G.nodes[neighbor]['type'] == 'consumer':
                        consumer = self.agents[neighbor]
                        capacity = self.G[node][neighbor]['capacity']
                        demand = consumer.demand - consumer.received
                        power_to_transmit = min(substation.load, demand, capacity)
                        consumer.received += power_to_transmit
                        substation.load -= power_to_transmit

    def analyze_results(self):
        total_generated = sum(agent.generated for agent in self.agents.values() if
                              isinstance(agent, ag.PowerPlant))
        total_consumed = sum(agent.received for agent in self.agents.values() if
                             isinstance(agent, ag.Consumer))
        unmet_demand = sum(agent.demand - agent.received for
                           agent in self.agents.values() if
                           isinstance(agent, ag.Consumer))

        total_payments = 0
        for node, agent in self.agents.items():
            if isinstance(agent, ag.Consumer):
                agent.calculate_payment()
                total_payments += agent.payment
        if self.verbose:
            print(f"Total Power Generated: {total_generated} MW")
            print(f"Total Power Consumed: {total_consumed} MW")
            print(f"Unmet Demand: {unmet_demand} MW")
            print(f"Total Payments: ${total_payments}")

            for node, agent in self.agents.items():
                if isinstance(agent, ag.PowerPlant):
                    print(f"{node}: Generated {agent.generated} MW")
                elif isinstance(agent, ag.Consumer):
                    print(f"{node}: Received {agent.received}/{agent.demand} MW, Payment: ${agent.payment}")
                elif isinstance(agent, ag.Substation):
                    print(f"{node}: Load {agent.load}/{agent.capacity} MW")
        return unmet_demand, total_generated, total_consumed, total_payments

    def calculate_costs(self):
        total_capital_cost = sum(agent.capital_cost for agent in self.agents.values() if
                                 isinstance(agent, ag.PowerPlant) or
                                 isinstance(agent, ag.Substation))
        total_operating_cost = sum(agent.operating_cost for agent in self.agents.values() if
                                   isinstance(agent, ag.PowerPlant) or
                                   isinstance(agent, ag.Substation))
        total_generation_cost = sum(agent.generated * agent.cost_per_mw for
                                    agent in self.agents.values() if
                                    isinstance(agent, ag.PowerPlant))

        if self.verbose:
            print(f"Total Capital Cost: ${total_capital_cost}")
            print(f"Total Operating Cost: ${total_operating_cost}")
            print(f"Total Generation Cost: ${total_generation_cost}")

        return total_capital_cost, total_operating_cost, total_generation_cost
