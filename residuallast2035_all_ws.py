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

ws = ["WS01", "WS02", "WS03", "WS04", "WS05", "WS06", "WS07", "WS08", "WS09", "WS10",
      "WS11", "WS12", "WS13", "WS14", "WS15", "WS16", "WS17", "WS18", "WS19", "WS20",
      "WS21", "WS22", "WS23", "WS24", "WS25", "WS26", "WS27", "WS28", "WS29", "WS30",
      "WS31", "WS32", "WS33", "WS34", "WS35", "WS36"]

LAST_FILE = "output/2035_load_all_ws.csv"
ERZEUGUNG_FILE = "output/erzeugung_2035_all_ws.csv"

last_df = pd.read_csv(LAST_FILE, na_values=['-'])
erzeugung_df = pd.read_csv(ERZEUGUNG_FILE, na_values=['-'])

last_df['Date'] = pd.to_datetime(last_df['Date'])
erzeugung_df['Date'] = pd.to_datetime(erzeugung_df['Date'])

last_df.set_index('Date', inplace=True)
erzeugung_df.set_index('Date', inplace=True)

residuallast_df = pd.DataFrame(index=last_df.index)

for w in ws:
    residuallast_df[w] = last_df[w] - erzeugung_df[w]

print(residuallast_df.head())
residuallast_df.to_csv('output/residuallast_2035_all_ws.csv')