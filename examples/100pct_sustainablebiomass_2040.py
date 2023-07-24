# -*- coding: utf-8 -*-

"""
General description
-------------------
This example shows how to perform a capacity optimization for
an energy system with storage. The following energy system is modeled (visualization not updated!)

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

# Read data file
filename = os.path.join(os.getcwd(), "uganda_sequences.csv")

data = pd.read_csv(filename)
number_timesteps = 24  # len(data)

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
price_lpg = 50
price_biomass = 1.042  # ask for different prices bagass e , biomass


# fossil_share = 0.2, we can do maximum biomass use; or required res_share!

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
epc_cooker_el = 10000
epc_stove_unimproved = 1000
epc_stove_improved = 4000
epc_lpg_stove = 1000
epc_combustion_engine_transport = 200000
epc_electric_transport = 250000

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

# create heat bus
bheat = solph.Bus(label="heat_bus")

# create transport bus
btrans = solph.Bus(label="transport_bus")

# create cooking bus
bcook = solph.Bus(label="cooking_bus")

# create biomass bus
bbm = solph.Bus(label='biomass_bus')

# create bagasse bus
bbg = solph.Bus(label='bagasse_bus')

# create lpg bus
blpg = solph.Bus(label='lpg_bus')

energysystem.add(bfuel, bel, bbm, bbg, bheat, btrans, bcook, bhg, blpg)

# create excess component for the electricity bus to allow overproduction
excess = solph.components.Sink(
    label="excess_bel", inputs={bel: solph.Flow()}
)

# create source object representing the fuel oil commodity
fuel_oil_resource = solph.components.Source(
    label="fuel_oil", outputs={bfuel: solph.Flow(nominal_value=1, variable_costs=price_fuel_oil)}
)  # nominal value is set to 1 to model continuous operation of fuel oil power plant
                # ominal_value=fossil_share
                #* consumption_total
                #/ 0.58
                #* number_timesteps
                #/ 8760,
                #full_load_time_max=1,
           #)

# create source object representing unsustainable biomass commodity
biomass_resource = solph.components.Source(
    label="biomass", outputs={bbm: solph.Flow(variable_costs=price_biomass)}
)

# create source object representing sustainable biomass commodity
bagasse_resource = solph.components.Source(
    label="bagasse", outputs={bbg: solph.Flow(variable_costs=price_biomass)}
)

# Begrenzung biomasse mit summed max
# create source object representing lpg commodity
lpg_resource = solph.components.Source(
    label="lpg", outputs={blpg: solph.Flow(variable_costs=price_lpg)}
)

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

# create simple transformer object representing a fuel oil plant
pp_fuel_oil = solph.components.Transformer(
    label="pp_fuel_oil",
    inputs={bfuel: solph.Flow()},
    outputs={
        bel: solph.Flow(   #  full_load_time_min=8760,
            variable_costs=3.4,
            investment=solph.Investment(ep_costs=epc_fuel_oil, existing=92, maximum=0)
            # see BAU is investment in oil possible?;
            # in RE scenario it is not an investment object -> maximum = 0
        )
    },
    conversion_factors={bel: 0.58},
)

# Bagasse Heat and Power Cogeneration Plant
pp_bagasse = solph.components.Transformer(
    label="pp_bagasse",
    inputs={bbg: solph.Flow()},
    outputs={
        bel: solph.Flow(
            variable_costs=5,
            investment=solph.Investment(ep_costs=epc_biomass/2, existing=112, maximum=1700)
        ),
        bheat: solph.Flow(
            variable_costs=5,
            investment=solph.Investment(ep_costs=epc_biomass/2, existing=112, maximum=1700)
        )
    },
    conversion_factors={bel: 0.35, bheat: 0.35},
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
    inputs={bhg: solph.Flow()},
    outputs={
        bel: solph.Flow(
            variable_costs=0,
            investment=solph.Investment(ep_costs=epc_fuel_cell)
        )
    },
    conversion_factors={bel: 0.6},
)

# create storage object representing a battery
battery_storage = solph.components.GenericStorage(
    label="battery",
    inputs={bel: solph.Flow(variable_costs=0)},
    outputs={bel: solph.Flow()},
    loss_rate=0.00,
    initial_storage_level=0,
    invest_relation_input_capacity=1,
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

# electric transport vehicles
transport_el = solph.components.Transformer(
    label="electric transport vehicles",
    inputs={bel: solph.Flow()},
    outputs={
        btrans: solph.Flow(
            variable_costs=0,
            investment=solph.Investment(ep_costs=epc_electric_transport)
        )
    },
    conversion_factors={btrans: 0.7},
)

# electric transport vehicles
transport_ce = solph.components.Transformer(
    label="combustion engine transport vehicles",
    inputs={bfuel: solph.Flow()},
    outputs={
        btrans: solph.Flow(
            variable_costs=0,
            investment=solph.Investment(ep_costs=epc_combustion_engine_transport)
        )
    },
    conversion_factors={btrans: 0.3},
)

# electric cookers
cooker_el = solph.components.Transformer(
    label="electric cookers",
    inputs={bel: solph.Flow()},
    outputs={
        bcook: solph.Flow(
            variable_costs=0,
            investment=solph.Investment(ep_costs=epc_cooker_el)
        )
    },
    conversion_factors={bcook: 0.665},
)

# unimproved stove

stove_unimproved = solph.components.Transformer(
    label="unimproved stoves",
    inputs={bbm: solph.Flow()},
    outputs={
        bcook: solph.Flow(
            variable_costs=0,
            investment=solph.Investment(ep_costs=epc_stove_unimproved)
        )
    },
    conversion_factors={bcook: 0.2},
)

# improved stove
stove_improved = solph.components.Transformer(
    label="improved stoves",
    inputs={bbm: solph.Flow()},
    outputs={
        bcook: solph.Flow(
            variable_costs=0,
            investment=solph.Investment(ep_costs=epc_stove_improved)
        )
    },
    conversion_factors={bcook: 0.5},
)

# LPG stove
stove_lpg = solph.components.Transformer(
    label="LPG stoves",
    inputs={blpg: solph.Flow()},
    outputs={
        bcook: solph.Flow(
            variable_costs=0,
            investment=solph.Investment(ep_costs=epc_lpg_stove)
        )
    },
    conversion_factors={bcook: 0.5},
)

# create simple sink object representing the electrical demand
demand_el = solph.components.Sink(
    label="electricity demand",
    inputs={bel: solph.Flow(fix=data["demand_el"], nominal_value=40500000)},
)

# create simple sink object representing the heat demand
demand_heat = solph.components.Sink(
    label="heat demand",
    inputs={bel: solph.Flow(fix=data["demand_heat"], nominal_value=40500000)},
)

# create simple sink object representing the cooking demand
demand_cooking = solph.components.Sink(
    label="cooking demand",
    inputs={bcook: solph.Flow(fix=data["demand_cooking"], nominal_value=40500000)},
)

demand_transport = solph.components.Sink(
    label="transport demand",
    inputs={btrans: solph.Flow(fix=data["demand_cooking"], nominal_value=40500000)},
)

# cooking demand, transport demand sinks!
energysystem.add(excess, fuel_oil_resource, biomass_resource, bagasse_resource, lpg_resource, wind, pv, hydro, demand_el, demand_cooking,
                 demand_transport, pp_fuel_oil, pp_bagasse, battery_storage, electrolyzer, fuel_cell, hydrogen_storage,
                 transport_el, transport_ce, cooker_el, stove_unimproved, stove_improved, stove_lpg)

##########################################################################
# Optimise the energy system
##########################################################################

logging.info("Optimise the energy system")

# initialise the operational model
om = solph.Model(energysystem)

# if tee_switch is true solver messages will be displayed
logging.info("Solve the optimization problem")
om.solve(solver="glpk", solve_kwargs={"tee": True})

##########################################################################
# Check and plot the results
##########################################################################

results = solph.processing.results(om)

electricity_bus = solph.views.node(results, "electricity")
heat_bus = solph.views.node(results, "heat_bus")
cooking_bus = solph.views.node(results, "cooking_bus")
transport_bus = solph.views.node(results, "transport_bus")

meta_results = solph.processing.meta_results(om)
pp.pprint(meta_results)

electricity_scalars = electricity_bus["scalars"]
heat_scalars = heat_bus["scalars"]
cooking_scalars = cooking_bus["scalars"]
transport_scalars = transport_bus["scalars"]
my_results = pd.concat([electricity_scalars, heat_scalars, cooking_scalars, transport_scalars], axis=0)

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
my_results.to_csv('scalars.csv')