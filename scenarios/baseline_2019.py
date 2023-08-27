
# -*- coding: utf-8 -*-

"""
General description
-------------------
Superstructure for Uganda Energy System. The superstructure includes all resources, power plants, vehicles,
 cooking devices which we make available for different energy pathways and scenarios.
 It is the base for all the scenarios we create.


Data
----
uganda_sequences.csv

Installation requirements
-------------------------
see README.md


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
# Energy Prices Uganda 2023 [$/MWh lower heating value]
price_fuel_oil = 88.9
price_biofuel = 64.1
price_kerosene = 99.8
price_lpg = 25.46
price_woody_biomass = 7.2
price_bagasse = 6.53
price_uranium = 3.4
price_peat = 2.78
price_waste_biomass = 1

# sustainable biomass limits (MWh)
tree_biomass_limit = 282272500
bush_biomass_limit = 11287500
papyrus_biomass_limit = 4837500
# fossil_share = 0.2, we can do maximum biomass use; or required res_share!

# If the period is one year the equivalent periodical costs (epc) of an
# investment are equal to the annuity. Use oemof's economic tools.
# EPC per MW installed as present value annual payments
epc_wind = 138172.5  # calculated before model; formula: economics.annuity (n=20, wacc=0.05)
epc_pv = 90345  # economics.annuity (n=20, wacc=0.05)
epc_hydro = 247500  # economics.annuity (n=20, wacc=0.05)
epc_battery = 21812.5  # economics.annuity (n=20, wacc=0.05)
epc_hydrogen_storage = 3937.5
epc_fuel_oil = 98000  # economics.annuity(capex=1000, n=20, wacc=0.05)
epc_peat = 187182.5  # economics.annuity(capex=1000, n=25, wacc=0.05)
epc_biomass = 206250  # sugarcane bagasse CHP
epc_electrolyzer = 50625  # hydrogen electrolyzer
epc_nuclear = 506192.5  # economics.annuity (n=50, wacc=0.05)
epc_geothermal = 330000
epc_fuel_cell = 71750
epc_cooker_el = 830
epc_biogas_heating = 3209
epc_industrial_boiler = 11000
epc_wood_boiler = 4000
epc_anaerobic_digester = 4437.5
epc_stove_unimproved = 52.5
epc_stove_improved = 262.5
epc_lpg_stove = 1300
epc_ethanol_stove = 1000
epc_combustion_engine_transport = 13937.5
epc_electric_transport = 20500
epc_hydrogen_transport = 17875
epc_kerosene_aviation = 650687.5
epc_hydrogen_aviation = 1000000


##########################################################################
# Create oemof objects
##########################################################################

logging.info("Create oemof objects")

# create fuel bus
bfuel = solph.Bus(label="fuel_bus")

# create biofuel bus
bbfuel = solph.Bus(label="biofuel_bus")

# create uranium bus
buran = solph.Bus(label="uranium_bus")

# create peat bus
bpeat = solph.Bus(label="peat_bus")

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

energysystem.add(bfuel, bbfuel, buran, bel, bpeat, borg, bks, bba, bbg, bheat, btrans, bavia, bcook, bhg, blpg, bwood)


# create source object representing the fuel oil commodity
fuel_oil_resource = solph.components.Source(
    label="fuel_oil", outputs={bfuel: solph.Flow(variable_costs=price_fuel_oil)}
)

# create biofuel source object
biofuel_resource = solph.components.Source(
    label="biofuel", outputs={bbfuel: solph.Flow(variable_costs=price_biofuel, nominal_value=1, max=1007)}
)

# create peat source object
peat_resource = solph.components.Source(
    label="peat", outputs={bpeat: solph.Flow(variable_costs=price_peat)}
)
# uranium resource
uranium_resource = solph.components.Source(
    label="uranium", outputs={buran: solph.Flow(variable_costs=price_uranium)}
)
# create source object representing tree biomass commodity
tree_biomass_resource = solph.components.Source(
    label="tree biomass", outputs={bwood: solph.Flow(variable_costs=price_woody_biomass)}
)
bush_resource = solph.components.Source(
    label="bush biomass", outputs={bwood: solph.Flow(variable_costs=price_woody_biomass)}
)
papyrus_resource = solph.components.Source(
    label="papyrus biomass", outputs={bwood: solph.Flow(variable_costs=price_woody_biomass)}
)
# create source object representing sustainable biomass commodity
bagasse_resource = solph.components.Source(
    label="bagasse", outputs={bba: solph.Flow(variable_costs=price_bagasse, nominal_value=1, max=726.4)}
)

vegetal_waste = solph.components.Source(
    label="vegetal waste", outputs={borg: solph.Flow(variable_costs=price_waste_biomass)}
    # sustainable harvest 1.2 Million tons
)

animal_waste = solph.components.Source(
    label="animal waste", outputs={borg: solph.Flow(variable_costs=price_waste_biomass)}
    # sustainable harvest 1 Million tons
)

human_waste = solph.components.Source(
    label="human waste", outputs={borg: solph.Flow(variable_costs=price_waste_biomass)}
    # sustainable harvest 1 Million tons
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
            fix=data["hydro"], variable_costs=3, nominal_value=1070
        )
    },
)

# create fixed source object representing geothermal power plants
geothermal = solph.components.Source(
    label="geothermal",
    outputs={
        bel: solph.Flow(
            variable_costs=30, nominal_value=0
        )
    },
)

# create fixed source object representing nuclear power plants
pp_nuclear = solph.components.Transformer(
    label="pp_nuclear",
    inputs={buran: solph.Flow()},
    outputs={
        bel: solph.Flow(full_load_time_min=number_timesteps,  # constant operation at rated power
                        variable_costs=13, investment=solph.Investment(ep_costs=epc_nuclear))
    },
    conversion_factors={bel: 0.33}
)

blender_biofuel = solph.components.Transformer(
    label="blender_biofuel",
    inputs={bbfuel: solph.Flow()},
    outputs={
        bfuel: solph.Flow(variable_costs=0.1, investment=solph.Investment(ep_costs=0, existing=0))
    })

# create simple transformer object representing a fuel oil plant
pp_fuel_oil = solph.components.Transformer(
    label="pp_fuel_oil",
    inputs={bfuel: solph.Flow()},
    outputs={
        bel: solph.Flow(full_load_time_min=number_timesteps,  # constant operation at rated power
                        variable_costs=3.4,
                        investment=solph.Investment(ep_costs=epc_fuel_oil, existing=92))
    },
    conversion_factors={bel: 0.375},
)

# create simple transformer object representing a fuel oil plant
pp_peat = solph.components.Transformer(
    label="pp_peat",
    inputs={bpeat: solph.Flow()},
    outputs={
        bel: solph.Flow(full_load_time_min=number_timesteps,  # constant operation at rated power
                        variable_costs=6.8,
                        investment=solph.Investment(ep_costs=epc_peat, existing=0))
    },
    conversion_factors={bel: 0.4},
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
    conversion_factors={bbg: 0.55},
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
    conversion_factors={bheat: 0.6},
)

# Industrial Boiler
industrial_boiler = solph.components.Transformer(
    label="industrial boiler",
    inputs={bfuel: solph.Flow()},
    outputs={
        bheat: solph.Flow(
            variable_costs=0,
            investment=solph.Investment(ep_costs=epc_industrial_boiler)
        )
    },
    conversion_factors={bheat: 0.6},
)

# Woody Biomass Boiler
wood_boiler = solph.components.Transformer(
    label="wood boiler",
    inputs={bwood: solph.Flow()},
    outputs={
        bheat: solph.Flow(
            variable_costs=0,
            investment=solph.Investment(ep_costs=epc_wood_boiler)
        )
    },
    conversion_factors={bheat: 0.5},
)

# Bagasse Heat and Power Cogeneration Plant
pp_bagasse = solph.components.Transformer(
    label="pp_bagasse",
    inputs={bba: solph.Flow(
        variable_costs=5, full_load_time_min=number_timesteps, nominal_value=112
    )},
    outputs={
        bel: solph.Flow(),
        bheat: solph.Flow()
    },
    conversion_factors={bel: 0.35, bheat: 0.35},
)

# Electrolyzer
electrolyzer = solph.components.Transformer(
    label="electrolyzer",
    inputs={bel: solph.Flow()},
    outputs={
        bhg: solph.Flow(
            variable_costs=0, nominal_value=0
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
            variable_costs=0, nominal_value=0
        )
    },
    conversion_factors={bel: 0.6},
)

# create storage object representing a battery
battery_storage = solph.components.GenericStorage(
    label="battery",
    inputs={bel: solph.Flow(variable_costs=0, nominal_value=0)},
    outputs={bel: solph.Flow()},
    loss_rate=0.00,
    initial_storage_level=0,
    invest_relation_input_capacity=1,
    invest_relation_output_capacity=1,
    inflow_conversion_factor=1,
    outflow_conversion_factor=0.86,
    investment=solph.Investment(ep_costs=epc_battery),
)

# create storage object representing a hydrogen storage
hydrogen_storage = solph.components.GenericStorage(
    label="hydrogen_storage",
    inputs={bhg: solph.Flow(variable_costs=0, nominal_value=0)},
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
            variable_costs=150, nominal_value=0,
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
            variable_costs=90,
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
            variable_costs=240, nominal_value=0,
        )
    },
    conversion_factors={btrans: 0.3},
)
# hydrogen airplanes
airplanes_hydrogen = solph.components.Transformer(
    label="hydrogen aviation",
    inputs={bhg: solph.Flow()},
    outputs={
        bavia: solph.Flow(
            variable_costs=180, nominal_value=0,
        )
    },
    conversion_factors={bavia: 0.3},
)
# kerosene airplanes
airplanes_kerosene = solph.components.Transformer(
    label="kerosene aviation",
    inputs={bks: solph.Flow()},
    outputs={
        bavia: solph.Flow(
            variable_costs=120,
            investment=solph.Investment(ep_costs=epc_kerosene_aviation)
        )
    },
    conversion_factors={bavia: 0.3},
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
     inputs={bfuel: solph.Flow(variable_costs=0)},
     outputs={bfuel: solph.Flow()},
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

# electric cookers
cooker_el = solph.components.Transformer(
    label="electric cookers",
    inputs={bel: solph.Flow()},
    outputs={
        bcook: solph.Flow(
            variable_costs=0, nominal_value=250.16  # 0.0055*38387
        )
    },
    conversion_factors={bcook: 0.8},
)

# unimproved stove

stove_unimproved = solph.components.Transformer(
    label="unimproved stoves",
    inputs={bwood: solph.Flow()},
    outputs={
        bcook: solph.Flow(
            variable_costs=0, nominal_value=31784  # 0.828*38387,
        )
    },
    conversion_factors={bcook: 0.135},
)

# improved stove
stove_improved = solph.components.Transformer(
    label="improved stoves",
    inputs={bwood: solph.Flow()},
    outputs={
        bcook: solph.Flow(
            variable_costs=0, nominal_value=5374  # 0.14*38387
        )
    },
    conversion_factors={bcook: 0.325},
)

# LPG stove
stove_lpg = solph.components.Transformer(
    label="LPG stoves",
    inputs={blpg: solph.Flow()},
    outputs={
        bcook: solph.Flow(
            variable_costs=0, nominal_value=499.0  # 0.013*38387
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
            variable_costs=0, nominal_value=211.13  # 0.0055*38387
        )
    },
    conversion_factors={bcook: 0.5},
)

# Ethanol cooker
stove_ethanol = solph.components.Transformer(
    label="ethanol stoves",
    inputs={bbfuel: solph.Flow()},
    outputs={
        bcook: solph.Flow(
            variable_costs=0, nominal_value=268.71  # 0.007*38387
        )
    },
    conversion_factors={bcook: 0.45},
)
# create simple sink object representing the electrical demand
demand_el = solph.components.Sink(
    label="electricity demand",
    inputs={bel: solph.Flow(fix=data["demand_el"], nominal_value=4168)},
)

# create simple sink object representing the heat demand
demand_heat = solph.components.Sink(
    label="heat demand",
    inputs={bheat: solph.Flow(fix=data["demand_heat"], nominal_value=2908)},
)

# create simple sink object representing excess electricty production allowing overproduction
excess_electricity = solph.components.Sink(
    label="excess_electricity",
    inputs={bel: solph.Flow()},
)

# create simple sink object representing the cooking demand
demand_cooking = solph.components.Sink(
    label="cooking demand",
    inputs={bcook: solph.Flow(fix=data["demand_cooking"], nominal_value=38387)},
)

demand_transport = solph.components.Sink(
    label="transport demand",
    inputs={btrans: solph.Flow(fix=data["demand_transport"], nominal_value=3990)},
)

demand_aviation = solph.components.Sink(
    label="aviation demand",
    inputs={bavia: solph.Flow(fix=data["demand_aviation"], nominal_value=154.0)},
)

# cooking demand, transport demand sinks!
energysystem.add(fuel_oil_resource, uranium_resource, biofuel_resource, tree_biomass_resource,
                 bush_resource, papyrus_resource, vegetal_waste, animal_waste, human_waste, bagasse_resource,
                 lpg_resource, kerosene_resource, wind, pv, hydro, geothermal, demand_el, demand_cooking,
                 demand_transport, demand_aviation, pp_fuel_oil, pp_nuclear, pp_bagasse, biogas_heating,
                 industrial_boiler, digester, battery_storage, electrolyzer, fuel_cell, hydrogen_storage,
                 transport_el, transport_ce, transport_hg, cooker_el, stove_unimproved, stove_improved, stove_lpg,
                 stove_biogas, stove_ethanol, infinite_wood_storage, infinite_kerosene_storage, infinite_lpg_storage,
                 infinite_biogas_storage, blender_biofuel, wood_boiler, infinite_fuel_storage, pp_peat, peat_resource,
                 excess_electricity, airplanes_kerosene, airplanes_hydrogen)

##########################################################################
# Visualize the energy system
##########################################################################

import graphviz
from oemof_visio import ESGraphRenderer

os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'
gr = ESGraphRenderer(energy_system=energysystem, filepath="superstructure_2040", img_format="png")
gr.view()

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

fuel_bus = solph.views.node(results, "fuel_bus")
electricity_bus = solph.views.node(results, "electricity")
heat_bus = solph.views.node(results, "heat_bus")
cooking_bus = solph.views.node(results, "cooking_bus")
transport_bus = solph.views.node(results, "transport_bus")
aviation_bus = solph.views.node(results, "aviation_bus")

meta_results = solph.processing.meta_results(om)
pp.pprint(meta_results)

# fuel_scalars = fuel_bus["scalars"] # create sum of sequences to see used fossil fuel and biofuel...
electricity_scalars = electricity_bus["scalars"]
heat_scalars = heat_bus["scalars"]
#  cooking_scalars = cooking_bus["scalars"]
transport_scalars = transport_bus["scalars"]
aviation_scalars = aviation_bus["scalars"]


electricity_sequences = electricity_bus["sequences"]
heat_sequences = heat_bus["sequences"]
cooking_sequences = cooking_bus["sequences"]
transport_sequences = transport_bus["sequences"]
aviation_sequences = aviation_bus["sequences"]

my_results = pd.concat([electricity_scalars, heat_scalars, transport_scalars, aviation_scalars],
                       axis=0)
sequences = pd.concat([electricity_sequences, heat_sequences, cooking_sequences, transport_sequences,
                       aviation_sequences], axis=1)
# installed capacity of storage in GWh
my_results["storage_invest_GWh"] = (
        results[(battery_storage, None)]["scalars"]["invest"] / 1e6
)

# installed capacity of wind power plant in MW
my_results["wind_invest_MW"] = (
        results[(wind, bel)]["scalars"]["invest"] / 1e3
)

print(results[(bcook, demand_cooking)]["sequences"].sum)
# resulting renewable energy share
tree_usage = results[(tree_biomass_resource, bwood)]["sequences"].sum()
float_tree_usage = float(tree_usage.iloc[0])
bush_usage = results[(tree_biomass_resource, bwood)]["sequences"].sum()
float_bush_usage = float(tree_usage.iloc[0])
papyrus_usage = results[(papyrus_resource, bwood)]["sequences"].sum()
float_papyrus_usage = float(papyrus_usage.iloc[0])

if float_tree_usage > tree_biomass_limit:
    unsustainable_tree_biomass = float_tree_usage - tree_biomass_limit
else:
    unsustainable_tree_biomass = 0
if float_bush_usage > bush_biomass_limit:
    unsustainable_bush_biomass = float_bush_usage - bush_biomass_limit
else:
    unsustainable_bush_biomass = 0
if float_papyrus_usage > bush_biomass_limit:
    unsustainable_papyrus_biomass = float_papyrus_usage - papyrus_biomass_limit
else:
    unsustainable_papyrus_biomass = 0

unsustainable_biomass = unsustainable_tree_biomass + unsustainable_bush_biomass + unsustainable_papyrus_biomass
total_woody_biomass = float_tree_usage + float_bush_usage + float_papyrus_usage
my_results["unsustainable_biomass_MWh"] = unsustainable_biomass
my_results["total_woody_biomass_MWh"] = total_woody_biomass
effective_end_use_stove_improved = results[(stove_improved, bcook)]["sequences"].sum()
effective_end_use_stove_unimproved = results[(stove_unimproved, bcook)]["sequences"].sum()
my_results["effective_end_use_stove_improved"] = effective_end_use_stove_improved
my_results["effective_end_use_stove_unimproved"] = effective_end_use_stove_unimproved
non_renewable_biomass_cooking = unsustainable_biomass/total_woody_biomass *\
                               (effective_end_use_stove_unimproved+effective_end_use_stove_improved)
my_results["non_renewable_biomass_cooking"] = non_renewable_biomass_cooking

# biofuel share
my_results["biofuel_share"] = (
    results[(blender_biofuel, bfuel)]["sequences"].sum()
    / (results[(blender_biofuel, bfuel)]["sequences"].sum()+results[(fuel_oil_resource, bfuel)]["sequences"].sum())
)

# RE share electricity production
my_results["RE_share_electricity production"] = (
        1
        - (results[(pp_fuel_oil, bel)]["sequences"].sum()
           + results[(pp_nuclear, bel)]["sequences"].sum()
           + results[(pp_peat, bel)]["sequences"].sum())
        / (results[(bel, demand_el)]["sequences"].sum() + results[(bel, excess_electricity)]["sequences"].sum()
           + results[(bel, cooker_el)]["sequences"].sum() + results[(bel, transport_el)]["sequences"].sum()
           + results[(bel, electrolyzer)]["sequences"].sum() - results[(fuel_cell, bel)]["sequences"].sum())
)
my_results["RE_share_effective_end_use_energy"] = (
        1
        - (results[(pp_fuel_oil, bel)]["sequences"].sum() + results[(pp_nuclear, bel)]["sequences"].sum()
           + results[(pp_peat, bel)]["sequences"].sum()
           + results[(stove_lpg, bcook)]["sequences"].sum() + results[(transport_ce, btrans)]["sequences"].sum()
           + results[(airplanes_kerosene, bavia)]["sequences"].sum() + non_renewable_biomass_cooking)
        / (results[(bel, demand_el)]["sequences"].sum() + results[(bel, excess_electricity)]["sequences"].sum()
           + results[(bel, transport_el)]["sequences"].sum()
           + results[(bel, electrolyzer)]["sequences"].sum() - results[(fuel_cell, bel)]["sequences"].sum()
           + results[(bcook, demand_cooking)]["sequences"].sum()
           + results[(btrans, demand_transport)]["sequences"].sum()
           + results[(bheat, demand_heat)]["sequences"].sum() + results[(bavia, demand_aviation)]["sequences"].sum()
           )
)

pp.pprint(my_results)
my_results.to_csv('baseline_2019_scalars.csv')
sequences.to_csv('baseline_2019_sequences.csv')
