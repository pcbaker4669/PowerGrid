# to make an executable:
# https://learnpython.com/blog/python-executable/#:~:text=Fortunately%2C%20PyInstaller%20(and%20similar%20programs,command%20line%20tool%20of%20choice.
# pyInstaller --onefile main.py
# pyInstaller --onefile --noconsole main.py

import matplotlib.pyplot as plt
import networkx as nx
import model

# Create the grid
power_model = model.Model(4, 4, 20)
grid = power_model.create_grid()

# Initialize agents
agents = power_model.initialize_agents()

# Simulate power flow
power_model.simulate_power_flow()

# Analyze results
power_model.analyze_results()

# Visualize the grid
pos = nx.spring_layout(grid)
node_colors = ['green' if grid.nodes[n]['type'] == 'plant' else 'blue' if grid.nodes[n]['type'] == 'substation' else 'red' for n in grid.nodes]
nx.draw(grid, pos, with_labels=True, node_color=node_colors)
plt.show()
