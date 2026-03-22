import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker

mpl.rcParams.update({
'figure.dpi': 150, 'axes.grid': True, 'grid.linestyle': '--',
'grid.alpha': 0.3, 'axes.edgecolor': 'black', 'axes.linewidth': 1.0,
'font.size': 20, 'font.family': 'serif', 'mathtext.fontset': 'stix',
'legend.frameon': False, 'xtick.direction': 'in', 'ytick.direction': 'in',
'xtick.minor.visible': False, 'ytick.minor.visible': True,
})

WS = "WS26"

# Importiere die Daten
PV_I_FILE = "input/DE00_CapacityFactors_PV_industrial_rooftop_2035.csv"
PV_R_FILE = "input/DE00_CapacityFactors_PV_residential_rooftop_2035.csv"
PC_U_FILE = "input/DE00_CapacityFactors_PV_utility_fixed_2035.csv"
WIND_ON_FILE = "input/DE00_CapacityFactors_Wind_Onshore_2035.csv"
WIND_OFF_FILE = "input/DE00_CapacityFactors_Wind_Offshore_2035.csv"

# Installed Capacity in MW
HYDRO = 3934
PV_I = 53520
PV_R = 119126
PV_U = 136354
WIND_ON = 157000
WIND_OFF = 50089

pv_i_df = pd.read_csv(PV_I_FILE, na_values=['-'])
pv_r_df = pd.read_csv(PV_R_FILE, na_values=['-'])
pc_u_df = pd.read_csv(PC_U_FILE, na_values=['-'])
wind_on_df = pd.read_csv(WIND_ON_FILE, na_values=['-'])
wind_off_df = pd.read_csv(WIND_OFF_FILE, na_values=['-'])

# Combine the "Date" and "Hour" columns into a single datetime column and set it as the index
for df in [pv_i_df, pv_r_df, pc_u_df, wind_on_df, wind_off_df]:
    hour = (df['Hour'] - 1).astype(str) 
    # if hour is less than 10, add a leading zero
    hour = hour.apply(lambda x: x.zfill(2))
    df['Date'] = pd.to_datetime(df['Date'] + '2018 ' + hour + ':00:00', format='%d.%m.%Y %H:%M:%S')
    df.set_index('Date', inplace=True)
    df.drop(columns=['Hour'], inplace=True)

# Calculate the total generation for each technology
generation_df = pd.DataFrame(index=pv_i_df.index)
generation_df['PV Industrial Rooftop'] = pv_i_df[WS] * PV_I
generation_df['PV Residential Rooftop'] = pv_r_df[WS] * PV_R
generation_df['PV Utility Fixed'] = pc_u_df[WS] * PV_U
generation_df['Wind Onshore'] = wind_on_df[WS] * WIND_ON
generation_df['Wind Offshore'] = wind_off_df[WS] * WIND_OFF
generation_df['Hydro'] = HYDRO * 0.5 # Assume 50% capacity factor for hydro

print(generation_df.head())

daily_generation = generation_df.resample('D').sum()

# convert to TWh
daily_generation = daily_generation / 1000000

# plot the daily values
fig, ax = plt.subplots(figsize=(15, 6))

start_date = pd.to_datetime("2018-01-01")
end_date = pd.to_datetime("2018-12-31")
ax.set_xlim(start_date, end_date)
ax.set_ylim(0, daily_generation.sum(axis=1).max() * 1.3)

# Only use german month names for x-axis labels
monate = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
ax.set_xticks(pd.date_range(start_date, end_date, freq='MS'))
ax.set_xticklabels(monate)

ax.stackplot(
    daily_generation.index,
    daily_generation['Hydro'],
    daily_generation['PV Industrial Rooftop'],
    daily_generation['PV Residential Rooftop'],
    daily_generation['PV Utility Fixed'],
    daily_generation['Wind Onshore'],
    daily_generation['Wind Offshore'],
    labels=['Wasserkraft', 'PV Industrie', 'PV Wohnen', 'PV Freifläche', 'Wind Onshore', 'Wind Offshore'],
    colors=['cyan','orange', 'green', 'blue', 'red', 'purple'],
    alpha=0.85
)
# Remove the first y-axis label
ax.set_yticks(ax.get_yticks()[1:])
ax.set_xlabel("Datum")
ax.set_ylabel("Energie [TWh]")
ax.set_title("Tägliche Erzeugung der Erneuerbaren Energien im Jahr 2035 - WS26")
# make legend with labels horizontal
ax.legend(loc='upper left', ncol=3) 
plt.tight_layout()
plt.show()

# Calculate the year-total production for all technologies
year_total_generation = daily_generation.sum()
year_total_all = year_total_generation.sum()
print(f"Year total generation: {year_total_all} TWh")

# Export the hourly total generation to a new CSV file with the columns "Date" and "Generation"
export_df = pd.DataFrame({
    "Date": generation_df.index,
    "Generation": generation_df.sum(axis=1)
})
export_df.to_csv("output/generation_2035_hourly.csv", index=False)

