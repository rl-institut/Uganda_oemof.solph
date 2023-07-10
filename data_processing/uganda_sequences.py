import pandas as pd

# Read CSV files
pv_df = pd.read_csv('solar-pv_profile.csv')
wind_df = pd.read_csv('wind-onshore_profile.csv')
hydro_df = pd.read_csv('hydro-ror_profile.csv')
demand_el_df = pd.read_csv('electricity-demand_profile.csv')
demand_heat_df = pd.read_csv('heat-demand_profile.csv')
demand_cooking_df = pd.read_csv('cooking-demand_profile.csv')
biomass_df = pd.read_csv('biomass-production_profile.csv')
fuel_oil_df = pd.read_csv('fuel-oil-production_profile.csv')

# Extract desired columns
pv = pv_df['pv']
wind = wind_df['wind']
hydro = hydro_df['hydro']
demand_el = demand_el_df['demand_el']
demand_heat = demand_heat_df['demand_heat']
demand_cooking = demand_cooking_df['demand_heat']
biomass_usage = biomass_df['biomass_production']
fuel_oil_usage = fuel_oil_df['fuel_oil_production']
# Add more columns as needed

# Create combined data frame
data_df = pd.DataFrame({
    'pv': pv,
    'wind': wind,
    'hydro': hydro,
    'demand_el': demand_el,
    'demand_heat': demand_heat,
    'demand_cooking': demand_cooking,
    'biomass_usage': biomass_usage,
    'fuel_oil_usage': fuel_oil_usage
})
print(data_df)
# Write combined data frame to CSV
data_df.to_csv('uganda_sequences.csv', index=False)
