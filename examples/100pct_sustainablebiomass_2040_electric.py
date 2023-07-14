# -*- coding: utf-8 -*-

"""
General description
-------------------
This example shows how to perform a capacity optimization for
an energy system with storage. The following energy system is modeled:

.. code-block:: text

                    input/output  bgas     bel
                         |          |        |
                         |          |        |
     wind(FixedSource)   |------------------>|
                         |          |        |
     pv(FixedSource)     |------------------>|
                         |          |        |
     gas_resource        |--------->|        |
     (Commodity)         |          |        |
                         |          |        |
     demand(Sink)        |<------------------|
                         |          |        |
                         |          |        |
     pp_gas(Transformer) |<---------|        |
                         |------------------>|
                         |          |        |
     storage(Storage)    |<------------------|
                         |------------------>|

The example exists in four variations. The following parameters describe
the main setting for the optimization variation 1:

    - optimize wind, pv, gas_resource and storage
    - set investment cost for wind, pv and storage
    - set gas price for kWh

    Results show an installation of wind and the use of the gas resource.
    A renewable energy share of 51% is achieved.

    Have a look at different parameter settings. There are four variations
    of this example in the same folder.

Data
----
uganda_sequences.csv

Installation requirements
-------------------------

This example requires oemof.solph (v0.5.x), install by:

    pip install oemof.solph[examples]


License
-------
`MIT license <https://github.com/oemof/oemof-solph/blob/dev/LICENSE>`_

"""

###############################################################################
# Imports
###############################################################################

import logging
import os
import pprint as pp
import warnings

import pandas as pd

# Default logger of oemof
# from oemof.tools import economics #  please use for epc cost
from oemof.tools import logger

from oemof import solph
from oemof.solph import helpers

# debug
debug = True  # Set number_of_timesteps to 3 to get a readable lp-file.
solver_verbose = False  # show/hide solver output

# Read data file
filename = os.path.join(os.getcwd(), "uganda_sequences.csv")

data = pd.read_csv(filename)
number_timesteps = 3  # len(data)

print(data)
##########################################################################
# Initialize the energy system and read/calculate necessary parameters
##########################################################################

logger.define_logging()
logging.info("Initialize the energy system")
date_time_index = solph.create_time_index(2021, number=number_timesteps)
energysystem = solph.EnergySystem(
    timeindex=date_time_index, infer_last_interval=False
)

price_fuel_oil = 37.9
price_biomass = 1.042

# If the period is one year the equivalent periodical costs (epc) of an
# investment are equal to the annuity. Use oemof's economic tools.
# EPC per MW installed
epc_wind = 138172.5  # calculated before model; formula: economics.annuity(capex=1000, n=20, wacc=0.05)
epc_pv = 90345  # economics.annuity(capex=1000, n=20, wacc=0.05)
epc_hydro = 247500  # economics.annuity(capex=1000, n=20, wacc=0.05)
epc_battery = 21812.5  # economics.annuity(capex=1000, n=20, wacc=0.05)
epc_hydrogen_storage = 3937.5
epc_fuel_oil = 98000  # economics.annuity(capex=1000, n=20, wacc=0.05)
epc_biomass = 206250  # sugarcane bagasse CHP
epc_electrolyzer = 50625  # hydrogen electrolyzer
epc_fuel_cell = 71750

##########################################################################
# Create oemof objects
##########################################################################

logging.info("Create oemof objects")

# create fuel oil bus
bfuel = solph.Bus(label="fuel_oil_bus")

# create electricity bus
bel = solph.Bus(label="electricity")

# create hydrogen bus
bhg = solph.Bus(label='hydrogen_bus')

# create biogas bus
bbm = solph.Bus(label='biomass_bus')

energysystem.add(bfuel, bel, bbm, bhg)

# create excess component for the electricity bus to allow overproduction
excess = solph.components.Sink(
    label="excess_bel", inputs={bel: solph.Flow()}
)

# create source object representing the fuel oil commodity
fuel_oil_resource = solph.components.Source(
    label="fuel_oil", outputs={bfuel: solph.Flow(fix=data["fuel_oil_usage"], nominal_value=92,
                                                 variable_costs=price_fuel_oil)}
)  # nominal value is set to 1 to model continuous operation of fuel oil power plant

# create source object representing the biogas commodity
biomass_resource = solph.components.Source(
    label="biomass", outputs={bbm: solph.Flow(fix=data["biomass_usage"], nominal_value=112,
                                              variable_costs=price_biomass)}
)  # nominal value is set to 1 to model continuous operation of fuel oil power plant

# create fixed source object representing wind power plants
wind = solph.components.Source(
    label="wind",
    outputs={
        bel: solph.Flow(
            fix=data["wind"],
            investment=solph.Investment(ep_costs=epc_wind),
        )
    },
)

# create fixed source object representing pv power plants
pv = solph.components.Source(
    label="pv",
    outputs={
        bel: solph.Flow(
            fix=data["pv"], investment=solph.Investment(ep_costs=epc_pv, existing=60)
        )
    },
)

# create fixed source object representing hydropower plants
hydro = solph.components.Source(
    label="hydro",
    outputs={
        bel: solph.Flow(
            fix=data["hydro"], variable_costs=3,
            investment=solph.Investment(ep_costs=epc_hydro, existing=1070, maximum=1930)  # in total the
            # maximum hydro potential is 3000 MW, please verify
        )
    },
)

# create simple sink object representing the electrical demand
demand_el = solph.components.Sink(
    label="electricity demand",
    inputs={bel: solph.Flow(fix=data["demand_el"], nominal_value=40500000)},
)

# create simple transformer object representing a fuel oil plant
pp_fuel_oil = solph.components.Transformer(
    label="pp_fuel_oil",
    inputs={bfuel: solph.Flow()},
    outputs={
        bel: solph.Flow(
            variable_costs=3.4  # summed_max=0.2*sum(data['demand_el'])

            # see BAU is investment in oil possible?;
            # in RE scenario it is not an investment object -> maximum = 0
        )
    },
    conversion_factors={bel: 0.58},
)

# Biomass Heat and Power Cogeneration Plant
pp_biomass = solph.components.Transformer(
    label="pp_biomass",
    inputs={bbm: solph.Flow()},
    outputs={
        bel: solph.Flow(
            variable_costs=5
        )
    },
    conversion_factors={bel: 0.35},
)

# Electrolyzer
electrolyzer = solph.components.Transformer(
    label="electrolyzer",
    inputs={bel: solph.Flow()},
    outputs={
        bhg: solph.Flow(
            variable_costs=0,
            investment=solph.Investment(ep_costs=epc_electrolyzer)
        )
    },
    conversion_factors={bhg: 0.665},
)

# Fuel Cell
fuel_cell = solph.components.Transformer(
    label="fuel_cell",
    inputs={bel: solph.Flow()},
    outputs={
        bhg: solph.Flow(
            variable_costs=0,
            investment=solph.Investment(ep_costs=epc_fuel_cell)
        )
    },
    conversion_factors={bhg: 0.6},
)

# create storage object representing a battery
battery_storage = solph.components.GenericStorage(
    label="battery",
    inputs={bel: solph.Flow(variable_costs=0)},
    outputs={bel: solph.Flow()},
    loss_rate=0.00,
    initial_storage_level=0,
    invest_relation_input_capacity=1,  # counting rate;it is the relation of charge per time step to total capacity
    invest_relation_output_capacity=1,
    inflow_conversion_factor=1,
    outflow_conversion_factor=0.9,
    investment=solph.Investment(ep_costs=epc_battery),
)

# create storage object representing a hydrogen storage
hydrogen_storage = solph.components.GenericStorage(
    label="hydrogen_storage",
    inputs={bhg: solph.Flow(variable_costs=0)},
    outputs={bhg: solph.Flow()},
    loss_rate=0.00,
    initial_storage_level=0,
    invest_relation_input_capacity=1,
    invest_relation_output_capacity=1,
    inflow_conversion_factor=1,
    outflow_conversion_factor=0.88,
    investment=solph.Investment(ep_costs=epc_hydrogen_storage),
)


energysystem.add(excess, fuel_oil_resource, biomass_resource, wind, pv, hydro, demand_el, pp_fuel_oil, pp_biomass,
                 battery_storage, electrolyzer, fuel_cell, hydrogen_storage)

##########################################################################
# Optimise the energy system
##########################################################################

logging.info("Optimise the energy system")

# initialise the operational model
om = solph.Model(energysystem)

# This is for debugging only. It is not(!) necessary to solve the problem
# and should be set to False to save time and disc space in normal use. For
# debugging the timesteps should be set to 3, to increase the readability
# of the lp-file.
filename = os.path.join(
    helpers.extend_basic_path("lp_files"), "sustainablebiomass_2040_electric.lp"
    )
logging.info("Store lp-file in {0}.".format(filename))
om.write(filename, io_options={"symbolic_solver_labels": True})

# if tee_switch is true solver messages will be displayed
logging.info("Solve the optimization problem")
om.solve(solver="glpk", solve_kwargs={"tee": True})


##########################################################################
# Check and plot the results
##########################################################################

# check if the new result object is working for custom components
results = solph.processing.results(om)

electricity_bus = solph.views.node(results, "electricity")

meta_results = solph.processing.meta_results(om)
pp.pprint(meta_results)

my_results = electricity_bus["scalars"]

# installed capacity of storage in GWh
my_results["storage_invest_GWh"] = (
        results[(battery_storage, None)]["scalars"]["invest"] / 1e6
)

# installed capacity of wind power plant in MW
my_results["wind_invest_MW"] = (
        results[(wind, bel)]["scalars"]["invest"] / 1e3
)

# resulting renewable energy share
my_results["res_share"] = (
        1
        - results[(pp_fuel_oil, bel)]["sequences"].sum()
        / results[(bel, demand_el)]["sequences"].sum()
)

pp.pprint(my_results)

#