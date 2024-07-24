import agents as ag
import networkx as nx
import random

# Set random seed for reproducibility (uncomment if needed)
random.seed(123456)

class Model:
    def __init__(self, num_plants=3, num_substations=2, num_consumers=5, extra_lines_req=0):
        self.G = nx.Graph()
        self.num_plants = num_plants
        self.num_substations = num_substations
        self.num_consumers = num_consumers
        self.agents = {}
        self.extra_lines_req = extra_lines_req
        self.extra_lines_used = 0

    # Step 1: Define the Grid Structure
    def create_grid(self):
        # Add power plants
        for i in range(self.num_plants):
            self.G.add_node(f'P{i}', type='plant', capacity=random.randint(50, 100))

        # Add substations with capacity
        for i in range(self.num_substations):
            self.G.add_node(f'S{i}', type='substation', capacity=random.randint(100, 200))

        # Add consumers
        for i in range(self.num_consumers):
            self.G.add_node(f'C{i}', type='consumer', demand=random.randint(5, 20))

        # Ensure each substation is connected to at least one power plant
        for substation in range(self.num_substations):
            plant = random.choice(range(self.num_plants))
            self.G.add_edge(f'P{plant}', f'S{substation}', capacity=random.randint(50, 100))

        # Additional connections from power plants to substations
        for plant in range(self.num_plants):
            connected = False
            for substation in range(self.num_substations):
                if self.G.has_edge(f'P{plant}', f'S{substation}'):
                    connected = True
                    break
            if not connected:
                # If the plant is not connected to any substation, connect it to a random substation
                substation = random.choice(range(self.num_substations))
                self.extra_lines_used += 1
                self.G.add_edge(f'P{plant}', f'S{substation}', capacity=random.randint(50, 100))

            # Optionally, add more connections from power plants to substations
        for plant in range(self.num_plants):
            if self.extra_lines_used < self.extra_lines_req:
                extra_to_add = self.extra_lines_req - self.extra_lines_used
                for _ in range(extra_to_add):
                    self.extra_lines_used += 1
                    substation = random.choice(range(self.num_substations))
                    self.G.add_edge(f'P{plant}', f'S{substation}', capacity=random.randint(50, 100))



        # Connect substations to consumers, edges (with transmission capacity)
        for consumer in range(self.num_consumers):
            substation = random.choice(range(self.num_substations))
            self.G.add_edge(f'S{substation}', f'C{consumer}', capacity=random.randint(20, 50))

        return self.G

    def initialize_agents(self):
        self.agents = {}
        for node, data in self.G.nodes(data=True):
            if data['type'] == 'plant':
                self.agents[node] = ag.PowerPlant(node, data['capacity'])
            elif data['type'] == 'substation':
                self.agents[node] = ag.Substation(node, data['capacity'])
            elif data['type'] == 'consumer':
                self.agents[node] = ag.Consumer(node, data['demand'])

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
                for neighbor in self.G.neighbors(node):
                    if self.G.nodes[neighbor]['type'] == 'substation':
                        substation = self.agents[neighbor]
                        capacity = self.G[node][neighbor]['capacity']
                        generated_power = min(plant.capacity - plant.generated, capacity)
                        plant.generated += generated_power
                        if substation.load + generated_power <= substation.capacity:
                            substation.load += generated_power
                        else:
                            available_capacity = substation.capacity - substation.load
                            plant.generated += available_capacity
                            substation.load += available_capacity

        # Distribute power from substations to consumers
        for node in self.G.nodes():
            if self.G.nodes[node]['type'] == 'substation':
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
        total_generated = sum(agent.generated for agent in self.agents.values() if isinstance(agent, ag.PowerPlant))
        total_consumed = sum(agent.received for agent in self.agents.values() if isinstance(agent, ag.Consumer))
        unmet_demand = sum(agent.demand - agent.received for agent in self.agents.values() if isinstance(agent, ag.Consumer))

        print(f"Total Power Generated: {total_generated} MW")
        print(f"Total Power Consumed: {total_consumed} MW")
        print(f"Unmet Demand: {unmet_demand} MW")

        for node, agent in self.agents.items():
            if isinstance(agent, ag.PowerPlant):
                print(f"{node}: Generated {agent.generated} MW")
            elif isinstance(agent, ag.Consumer):
                print(f"{node}: Received {agent.received}/{agent.demand} MW")
            elif isinstance(agent, ag.Substation):
                print(f"{node}: Load {agent.load}/{agent.capacity} MW")
