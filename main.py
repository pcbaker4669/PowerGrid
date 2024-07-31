# to make an executable:
# https://learnpython.com/blog/python-executable/#:~:text=Fortunately%2C%20PyInstaller%20(and%20similar%20programs,command%20line%20tool%20of%20choice.
# pyInstaller --onefile main.py
# pyInstaller --onefile --noconsole main.py
# Matplotlib -- https://www.youtube.com/playlist?list=PL-osiE80TeTvipOqomVEeZ1HRrcEvtZB_

import matplotlib.pyplot as plt
import networkx as nx
import model
from tkinter import *
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg
)

root = Tk()
root.title("Simple Power Grid Model")
fig = plt.figure(frameon=True, figsize=(5, 5), dpi=100)
canvas = FigureCanvasTkAgg(fig, root)

widget_frm = Frame(root)
widget_frm.grid(row=0, column=0)

# tk controls
control_frm = LabelFrame(widget_frm, text="ModelParameters")
control_frm.grid(row=0, column=0, pady=5)
output_frm = LabelFrame(widget_frm, text="Output")
output_frm.grid(row=1, column=0, pady=5)

# Model Parameters
num_plants_vint = IntVar()
num_plants_vint.set(2)
num_plants_lbl = Label(control_frm, text="Plants:")
num_plants_lbl.grid(row=0, column=0)
num_plants_ent = Entry(control_frm, textvariable=num_plants_vint)
num_plants_ent.grid(row=0, column=1)

# number of substations
num_subs_vint = IntVar()
num_subs_vint.set(2)
num_subs_lbl = Label(control_frm, text="Substations:")
num_subs_lbl.grid(row=1, column=0)
num_subs_ent = Entry(control_frm, textvariable=num_subs_vint)
num_subs_ent.grid(row=1, column=1)

# number of customers
num_cust_vint = IntVar()
num_cust_vint.set(10)
num_cust_lbl = Label(control_frm, text="Customers:")
num_cust_lbl.grid(row=2, column=0)
num_cust_ent = Entry(control_frm, textvariable=num_cust_vint)
num_cust_ent.grid(row=2, column=1)

# extra lines used in model
num_extra_lines_vint = IntVar()
num_extra_lines_vint.set(2)
num_extra_lines_lbl = Label(control_frm, text="Extra Lines:")
num_extra_lines_lbl.grid(row=3, column=0)
num_extra_lines_ent = Entry(control_frm, textvariable=num_extra_lines_vint)
num_extra_lines_ent.grid(row=3, column=1)

# Output
# Unmet Demand
unmet_demand_vint = IntVar()
unmet_demand_vint.set(0)
unmet_demand_lbl = Label(output_frm, text="Unmet Demand (MW):")
unmet_demand_lbl.grid(row=0, column=0)
unmet_demand_ent = Entry(output_frm, textvariable=unmet_demand_vint)
unmet_demand_ent.grid(row=0, column=1)

# Total Generated
tot_gen_vint = IntVar()
tot_gen_vint.set(0)
tot_gen_lbl = Label(output_frm, text="Total Generated (MW):")
tot_gen_lbl.grid(row=1, column=0)
tot_gen_ent = Entry(output_frm, textvariable=tot_gen_vint)
tot_gen_ent.grid(row=1, column=1)

# Total Consumed
tot_consumed_vint = IntVar()
tot_consumed_vint.set(0)
tot_consumed_lbl = Label(output_frm, text="Total Consumed (MW):")
tot_consumed_lbl.grid(row=2, column=0)
tot_consumed_ent = Entry(output_frm, textvariable=tot_consumed_vint)
tot_consumed_ent.grid(row=2, column=1)

# Grid Capital cost
tot_cap_cost_vint = IntVar()
tot_cap_cost_vint.set(0)
tot_cap_cost_lbl = Label(output_frm, text="Total Capital Cost ($):")
tot_cap_cost_lbl.grid(row=3, column=0)
tot_cap_cost_ent = Entry(output_frm, textvariable=tot_cap_cost_vint)
tot_cap_cost_ent.grid(row=3, column=1)

# Grid Operational cost
tot_op_cost_vint = IntVar()
tot_op_cost_vint.set(0)
tot_op_cost_lbl = Label(output_frm, text="Total Operational Cost ($):")
tot_op_cost_lbl.grid(row=4, column=0)
tot_op_cost_ent = Entry(output_frm, textvariable=tot_op_cost_vint)
tot_op_cost_ent.grid(row=4, column=1)

# Grid Operational cost
tot_per_mw_cost_vint = IntVar()
tot_per_mw_cost_vint.set(0)
tot_per_mw_cost_lbl = Label(output_frm, text="Total Per/MW Cost ($):")
tot_per_mw_cost_lbl.grid(row=5, column=0)
tot_per_mw_cost_ent = Entry(output_frm, textvariable=tot_per_mw_cost_vint)
tot_per_mw_cost_ent.grid(row=5, column=1)

# Total Payments by Consumers
tot_payments_vint = IntVar()
tot_payments_vint.set(0)
tot_payments_lbl = Label(output_frm, text="Total Payments ($):")
tot_payments_lbl.grid(row=6, column=0)
tot_payments_ent = Entry(output_frm, textvariable=tot_payments_vint)
tot_payments_ent.grid(row=6, column=1)



run_btn = Button(widget_frm, text="Run", command=lambda: run())
run_btn.grid(row=2, column=0, pady=5)


def run():
    plt.clf()
    # Create the grid
    power_model = model.Model(num_plants_vint.get(), num_subs_vint.get(),
                              num_cust_vint.get(), num_extra_lines_vint.get())
    grid = power_model.create_grid()
    # Initialize agents
    agents = power_model.initialize_agents()
    # Simulate power flow
    power_model.simulate_power_flow()
    # Analyze results
    costs = power_model.calculate_costs()
    tot_cap_cost_vint.set(costs[0])
    tot_cap_cost_ent.configure(textvariable=tot_cap_cost_vint)
    tot_op_cost_vint.set(costs[1])
    tot_op_cost_ent.configure(textvariable=tot_op_cost_vint)
    tot_per_mw_cost_vint.set(costs[2])
    tot_per_mw_cost_ent.configure(textvariable=tot_per_mw_cost_vint)

    vals = power_model.analyze_results()
    unmet_demand_vint.set(vals[0])
    unmet_demand_ent.configure(textvariable=unmet_demand_vint)
    tot_gen_vint.set(vals[1])
    tot_gen_ent.configure(textvariable=tot_gen_vint)
    tot_consumed_vint.set(vals[2])
    tot_consumed_ent.configure(textvariable=tot_consumed_vint)
    tot_payments_vint.set(vals[3])
    tot_payments_ent.configure(textvariable=tot_payments_vint)

    # Visualize the grid
    pos = nx.spring_layout(grid)

    node_colors = []

    for n in grid.nodes:
        if grid.nodes[n]['type'] == 'plant':
            node_colors.append('green')
        elif grid.nodes[n]['type'] == 'substation':
            node_colors.append('blue')
        elif grid.nodes[n]['type'] == 'consumer':
            consumer = agents[n]
            if consumer.received >= consumer.demand:
                node_colors.append('red')
            else:
                node_colors.append('darkgray')

    nx.draw(grid, pos, with_labels=True, node_color=node_colors)
    canvas.draw()
    canvas.flush_events()


canvas.get_tk_widget().grid(row=0, column=2)


def exit_model():
    root.quit()


run()

root.protocol("WM_DELETE_WINDOW", exit_model)
root.mainloop()
