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

print(data.head())
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
price_biofuel = 25
price_kerosene = 55
price_lpg = 50
price_biomass = 1.042  # ask for different prices bagass e , biomass


# fossil_share = 0.2, we can do maximum biomass use; or required res_share!

# If the period is one year the equivalent periodical costs (epc) of an
# investment are equal to the annuity. Use oemof's economic tools.
# EPC per MW installed as present value annual payments
epc_wind = 138172.5  # calculated before model; formula: economics.annuity(capex=1000, n=20, wacc=0.05)
epc_pv = 90345  # economics.annuity(capex=1000, n=20, wacc=0.05)
epc_hydro = 247500  # economics.annuity(capex=1000, n=20, wacc=0.05)
epc_battery = 21812.5  # economics.annuity(capex=1000, n=20, wacc=0.05)
epc_hydrogen_storage = 3937.5
epc_fuel_oil = 98000  # economics.annuity(capex=1000, n=20, wacc=0.05)
epc_biomass = 206250  # sugarcane bagasse CHP
epc_electrolyzer = 50625  # hydrogen electrolyzer
epc_geothermal = 400000
epc_fuel_cell = 71750
epc_cooker_el = 10000
epc_biogas_heating = 10000
epc_anaerobic_digester = 30000
epc_stove_unimproved = 1000
epc_stove_improved = 4000
epc_lpg_stove = 1000
epc_combustion_engine_transport = 20000
epc_electric_transport = 250000
epc_hydrogen_transport = 40000
epc_aviation = 50000
epc_shipping = 40000

##########################################################################
# Create oemof objects
##########################################################################

logging.info("Create oemof objects")

# create fuel bus
bfuel = solph.Bus(label="fuel_bus")

# create kerosene bus
bks = solph.Bus(label="kerosene_bus")

# create electricity bus
bel = solph.Bus(label="electricity")

# create hydrogen bus
bhg = solph.Bus(label='hydrogen_bus')

# create heat bus
bheat = solph.Bus(label="heat_bus")

# create transport bus
btrans = solph.Bus(label="transport_bus")

# create aviation bus
bavia = solph.Bus(label="aviation_bus")

# create shipping bus
bship = solph.Bus(label="shipping_bus")

# create woody biomass bus
bwood = solph.Bus(label="woody_biomass_bus")

# create organic waste bus
borg = solph.Bus(label="organic_waste_bus")

# create biogas bus
bbg = solph.Bus(label='biogas_bus')

# create cooking bus
bcook = solph.Bus(label="cooking_bus")

# create bagasse bus
bba = solph.Bus(label='bagasse_bus')

# create lpg bus
blpg = solph.Bus(label='lpg_bus')

energysystem.add(bfuel, bel, bwood, borg, bks, bba, bbg, bheat, btrans, bavia, bship, bcook, bhg, blpg, bwood)

# create excess component for the electricity bus to allow overproduction
excess = solph.components.Sink(
    label="excess_bel", inputs={bel: solph.Flow()}
)

# create source object representing the fuel oil commodity
fuel_oil_resource = solph.components.Source(
    label="fuel_oil", outputs={bfuel: solph.Flow(nominal_value=1, variable_costs=price_fuel_oil)}
)  # nominal value is set to 1 to model continuous operation of fuel oil power plant
                # nominal_value=fossil_share
                #* consumption_total
                #/ 0.58
                #* number_timesteps
                #/ 8760,
                #full_load_time_max=1,
           #)
# create biofuel source object
biofuel_resource = solph.components.Source(
    label="biofuel", outputs={bfuel: solph.Flow(nominal_value=1, variable_costs=price_biofuel)}
)
# create source object representing unsustainable biomass commodity
tree_biomass_resource = solph.components.Source(
    label="tree biomass", outputs={bwood: solph.Flow(variable_costs=price_biomass)} #sustainable harvest 26.3 Million tons
)
bush_resource = solph.components.Source(
    label="bush biomass", outputs={bwood: solph.Flow(variable_costs=price_biomass)} #sustainable harvest 10.5 Million tons
)
papyrus_resource = solph.components.Source(
    label="papyrus biomass", outputs={bwood: solph.Flow(variable_costs=price_biomass)} #sustainable harvest 4.5 Million tons
)
# create source object representing sustainable biomass commodity
bagasse_resource = solph.components.Source(
    label="bagasse", outputs={bba: solph.Flow(variable_costs=price_biomass)} #sustainable harvest 1.4 Million tons
)

vegetal_waste = solph.components.Source(
    label="vegetal waste", outputs={borg: solph.Flow(variable_costs=price_biomass)} #sustainable harvest 1.2 Million tons
)

animal_waste = solph.components.Source(
    label="animal waste", outputs={borg: solph.Flow(variable_costs=price_biomass)} #sustainable harvest 1 Million tons
)

human_waste = solph.components.Source(
    label="human waste", outputs={borg: solph.Flow(variable_costs=price_biomass)} #sustainable harvest 1 Million tons
)


# Begrenzung biomasse mit summed max
# create source object representing lpg commodity
lpg_resource = solph.components.Source(
    label="lpg", outputs={blpg: solph.Flow(variable_costs=price_lpg)}
)

kerosene_resource = solph.components.Source(
    label="kerosene", outputs={bks: solph.Flow(variable_costs=price_kerosene)}
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

# create fixed source object representing geothermal power plants
geothermal = solph.components.Source(
    label="geothermal",
    outputs={
        bel: solph.Flow(
            variable_costs=30,
            investment=solph.Investment(ep_costs=epc_geothermal, maximum=1500)  # in total the
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

# Anaerobic Digester
digester = solph.components.Transformer(
    label="digester",
    inputs={borg: solph.Flow()},
    outputs={
        bbg: solph.Flow(
            variable_costs=0,
            investment=solph.Investment(ep_costs=epc_anaerobic_digester)
        )
    },
    conversion_factors={bbg: 0.6},
)
# Biogas Heating Unit (Chick breeding)
biogas_heating = solph.components.Transformer(
    label="biogas heating",
    inputs={bbg: solph.Flow()},
    outputs={
        bheat: solph.Flow(
            variable_costs=0,
            investment=solph.Investment(ep_costs=epc_biogas_heating)
        )
    },
    conversion_factors={bheat: 0.9},
)
# Bagasse Heat and Power Cogeneration Plant
pp_bagasse = solph.components.Transformer(
    label="pp_bagasse",
    inputs={bba: solph.Flow()},
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
    conversion_factors={bel: 0.35, bheat: 0.65},
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

# combustion engine transport vehicles
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

# hydrogen vehicles
transport_hg = solph.components.Transformer(
    label="hydrogen vehicles",
    inputs={bhg: solph.Flow()},
    outputs={
        btrans: solph.Flow(
            variable_costs=0,
            investment=solph.Investment(ep_costs=epc_hydrogen_transport)
        )
    },
    conversion_factors={btrans: 0.3},
)
# airplanes
aviation = solph.components.Transformer(
    label="aviation",
    inputs={bks: solph.Flow()},
    outputs={
        bavia: solph.Flow(
            variable_costs=0,
            investment=solph.Investment(ep_costs=epc_aviation)
        )
    },
    conversion_factors={bavia: 0.7},
)

infinite_wood_storage = solph.components.GenericStorage(
    label="infinite biomass storage",
    inputs={bwood: solph.Flow(variable_costs=0)},
    outputs={bwood: solph.Flow()},
    loss_rate=0.00,
    initial_storage_level=0,
    invest_relation_input_capacity=1,
    invest_relation_output_capacity=1,
    inflow_conversion_factor=1,
    outflow_conversion_factor=1,
    investment=solph.Investment(ep_costs=0),
)

# infinite and free storage kerosene
infinite_kerosene_storage = solph.components.GenericStorage(
    label="infinite kerosene storage",
    inputs={bks: solph.Flow(variable_costs=0)},
    outputs={bks: solph.Flow()},
    loss_rate=0.00,
    initial_storage_level=0,
    invest_relation_input_capacity=1,
    invest_relation_output_capacity=1,
    inflow_conversion_factor=1,
    outflow_conversion_factor=1,
    investment=solph.Investment(ep_costs=0),
)

# infinite and free storage fuel oil
infinite_fuel_storage = solph.components.GenericStorage(
    label="infinite fuel oil storage",
    inputs={bks: solph.Flow(variable_costs=0)},
    outputs={bks: solph.Flow()},
    loss_rate=0.00,
    initial_storage_level=0,
    invest_relation_input_capacity=1,
    invest_relation_output_capacity=1,
    inflow_conversion_factor=1,
    outflow_conversion_factor=1,
    investment=solph.Investment(ep_costs=0),
)
# infinite and free storage lpg
infinite_lpg_storage = solph.components.GenericStorage(
    label="infinite lpg storage",
    inputs={blpg: solph.Flow(variable_costs=0)},
    outputs={blpg: solph.Flow()},
    loss_rate=0.00,
    initial_storage_level=0,
    invest_relation_input_capacity=1,
    invest_relation_output_capacity=1,
    inflow_conversion_factor=1,
    outflow_conversion_factor=1,
    investment=solph.Investment(ep_costs=0),
)
# infinite and free storage biogas
infinite_biogas_storage = solph.components.GenericStorage(
    label="infinite biogas storage",
    inputs={bbg: solph.Flow(variable_costs=0)},
    outputs={bbg: solph.Flow()},
    loss_rate=0.00,
    initial_storage_level=0,
    invest_relation_input_capacity=1,
    invest_relation_output_capacity=1,
    inflow_conversion_factor=1,
    outflow_conversion_factor=1,
    investment=solph.Investment(ep_costs=0),
)

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
    inputs={bwood: solph.Flow()},
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
    inputs={bwood: solph.Flow()},
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

# Biogas Cooker
stove_biogas = solph.components.Transformer(
    label="biogas stoves",
    inputs={bbg: solph.Flow()},
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

demand_aviation = solph.components.Sink(
    label="aviation demand",
    inputs={bavia: solph.Flow(fix=data["demand_cooking"], nominal_value=40500000)},
)

# cooking demand, transport demand sinks!
energysystem.add(excess, fuel_oil_resource, biofuel_resource, tree_biomass_resource, bush_resource, papyrus_resource, vegetal_waste,
                 animal_waste, human_waste, bagasse_resource, lpg_resource, kerosene_resource, wind,
                 pv, hydro, geothermal, demand_el, demand_cooking, demand_transport, demand_aviation, pp_fuel_oil,
                 pp_bagasse, biogas_heating, digester, battery_storage, electrolyzer, fuel_cell, aviation,
                 hydrogen_storage, transport_el, transport_ce, transport_hg, cooker_el, stove_unimproved, stove_improved, stove_lpg,
                 stove_biogas, infinite_wood_storage, infinite_kerosene_storage, infinite_lpg_storage,
                 infinite_fuel_storage, infinite_biogas_storage)

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

#fuel_bus = solph.views.node(results, "fuel_bus")
electricity_bus = solph.views.node(results, "electricity")
heat_bus = solph.views.node(results, "heat_bus")
cooking_bus = solph.views.node(results, "cooking_bus")
transport_bus = solph.views.node(results, "transport_bus")
aviation_bus = solph.views.node(results, "aviation_bus")
shipping_bus = solph.views.node(results, "shipping_bus")

meta_results = solph.processing.meta_results(om)
pp.pprint(meta_results)

#fuel_scalars = fuel_bus["scalars"] # create sum of sequences to see used fossil fuel and biofuel...
electricity_scalars = electricity_bus["scalars"]
heat_scalars = heat_bus["scalars"]
cooking_scalars = cooking_bus["scalars"]
transport_scalars = transport_bus["scalars"]
aviation_scalars = aviation_bus["scalars"]
#shipping_scalars = shipping_bus["scalars"]

my_results = pd.concat([electricity_scalars, heat_scalars, cooking_scalars, transport_scalars, aviation_scalars], axis=0)

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
