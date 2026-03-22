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

ws = ["WS01", "WS02", "WS03", "WS04", "WS05", "WS06", "WS07", "WS08", "WS09", "WS10",
      "WS11", "WS12", "WS13", "WS14", "WS15", "WS16", "WS17", "WS18", "WS19", "WS20",
      "WS21", "WS22", "WS23", "WS24", "WS25", "WS26", "WS27", "WS28", "WS29", "WS30",
      "WS31", "WS32", "WS33", "WS34", "WS35", "WS36"]

all_ws = pd.DataFrame(index=pv_i_df.index)

for w in ws:
    generation_df = pd.DataFrame(index=pv_i_df.index)
    generation_df['PV Industrial Rooftop'] = pv_i_df[w].values * PV_I
    generation_df['PV Residential Rooftop'] = pv_r_df[w].values * PV_R
    generation_df['PV Utility Fixed'] = pc_u_df[w].values * PV_U
    generation_df['Wind Onshore'] = wind_on_df[w].values * WIND_ON
    generation_df['Wind Offshore'] = wind_off_df[w].values * WIND_OFF
    generation_df['Hydro'] = HYDRO * 0.5 # Assume 50% capacity factor for hydro
    all_ws[w] = generation_df.sum(axis=1)

print(all_ws.head())
all_ws.to_csv('output/erzeugung_2035_all_ws.csv')
