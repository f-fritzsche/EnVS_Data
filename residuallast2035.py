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

LAST_FILE = "average_load_2035.csv"
ERZEUGUNG_FILE = "generation_2035_hourly.csv"

last_df = pd.read_csv(LAST_FILE, na_values=['-'])
erzeugung_df = pd.read_csv(ERZEUGUNG_FILE, na_values=['-'])

last_df['Date'] = pd.to_datetime(last_df['Date'])
erzeugung_df['Date'] = pd.to_datetime(erzeugung_df['Date'])

last_df.set_index('Date', inplace=True)
erzeugung_df.set_index('Date', inplace=True)


# Calculate the Residuallast
residuallast_df = last_df['Load'] - erzeugung_df['Generation']

# Export the Residuallast to a new CSV file
residuallast_df.to_csv("residuallast_2035.csv", header=['Residuallast'], index=True)

daily_residuallast = residuallast_df.resample('D').sum()

daily_residuallast = daily_residuallast / 1000000 # convert to TWh

# Calculate the "above zero" and "below zero" parts of the residual load for better visualization
daily_residuallast_above_zero = daily_residuallast.copy()
daily_residuallast_below_zero = daily_residuallast.copy()
daily_residuallast_above_zero[daily_residuallast_above_zero < 0] = 0
daily_residuallast_below_zero[daily_residuallast_below_zero > 0] = 0

# Sum the positive and negative parts for the entire year to check if they balance out
total_residuallast_above_zero = daily_residuallast_above_zero.sum()
total_residuallast_below_zero = daily_residuallast_below_zero.sum()
print(f"Total Residual Load above zero: {total_residuallast_above_zero} TWh")
print(f"Total Residual Load below zero: {total_residuallast_below_zero} TWh")

# Plotting
fig, ax = plt.subplots(figsize=(15, 6))

start_date = pd.to_datetime("2018-01-01")
end_date = pd.to_datetime("2018-12-31")
ax.set_xlim(start_date, end_date)

# Make the y = 0 line more visible
ax.axhline(0, color='black', linewidth=0.8, linestyle='--')

# Only use german month names for x-axis labels
monate = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']

ax.set_xticks(pd.date_range(start_date, end_date, freq='MS'))
ax.set_xticklabels(monate)
ax.plot(daily_residuallast.index, daily_residuallast, color='red', linewidth=1.8)
ax.set_xlabel("Datum")
ax.set_ylabel("Energie [TWh]")
ax.set_title("Tägliche Residualenergie im Jahr 2035")
plt.tight_layout()
plt.show()
