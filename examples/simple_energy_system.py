# simple energy system model
import math

from oemof.tools import logger
from oemof import solph


import os
import pandas as pd
import pprint as pp
import numpy as np

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
# *********************************************************************************************
# set up oemof.solph
# *********************************************************************************************

solver = "cbc"
debug =True  # Set number_of_timesteps to 3 to get a readable lp-file.
number_of_time_steps = 8760
solver_verbose = False  # show/hide solver output
infer_last_interval = False
# initiate the logger (see the API docs for more information)
logger.define_logging()
print(number_of_time_steps)

logger.info("Initialize the iWEFEs system")
date_time_index = pd.date_range(
    "1/1/2020", periods=number_of_time_steps, freq="H")

es = solph.EnergySystem(timeindex=date_time_index)
print(date_time_index)

# *********************************************************************************************
# Create oemof objects (bus, sink , source, transformer....)
# *********************************************************************************************

# Electricity bus
bus_elec = solph.Bus(label="electricity")

# Hydrogen bus
bus_h2 = solph.Bus(label="hydrogen")

# Heat bus
bus_heat = solph.Bus(label="heat")

# Add the buses to the energy system
es.add(bus_elec, bus_h2, bus_heat)

# Define the components in the energy system

# Wind turbine
wind = solph.components.Source(
    label="wind",
    outputs={bus_elec: solph.Flow(fix=True, nominal_value=100)}
)

# Photovoltaics
pv = solph.components.Source(
    label="pv",
    outputs={bus_elec: solph.Flow(fix=True, nominal_value=50)}
)

# Hydrogen production from excess electricity
h2_production = solph.components.Transformer(
    label="h2_production",
    inputs={bus_elec: solph.Flow()},
    outputs={bus_h2: solph.Flow()},
    conversion_factors={bus_h2: 0.7}
)

# Hydrogen storage
h2_storage = solph.components.GenericStorage(
    label="h2_storage",
    inputs={bus_h2: solph.Flow()},
    outputs={bus_h2: solph.Flow()},
    loss_rate=0.01,
    initial_storage_level=0.5,
    max_storage_level=1
)

# Hydrogen to electricity conversion
h2_to_elec = solph.components.Transformer(
    label="h2_to_elec",
    inputs={bus_h2: solph.Flow()},
    outputs={bus_elec: solph.Flow()},
    conversion_factors={bus_elec: 0.6}
)

# Biogas cogeneration
biogas = solph.components.Transformer(
    label="biogas",
    inputs={bus_elec: solph.Flow()},
    outputs={bus_heat: solph.Flow(), bus_elec: solph.Flow()},
    conversion_factors={bus_heat: 0.5, bus_elec: 0.4}
)

# Battery storage
#battery = solph.components.GenericStorage(
#    label="battery",
#    inputs={bus_elec: solph.Flow()},
#    outputs={bus_elec: solph.Flow()},
#    loss_rate=0.01,
#    initial_storage_level=0.5,
#    max_storage_level=1
#)

# Add the components to the energy system
es.add(wind, pv, h2_production, h2_storage, h2_to_elec, biogas)

# Define the optimization problem
om = solph.Model(es)

# Solve the optimization problem
om.solve()
logger.info("Optimise the energy system")

# initialise the operational model
model = solph.Model(es)
