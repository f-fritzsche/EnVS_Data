import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker

# Netzlast
LAST = "Netzlast [MWh]"

# Erzeugung
ERNEUERBARE = ["Biomasse [MWh]", "Wasserkraft [MWh]", "Wind Offshore [MWh]", "Wind Onshore [MWh]", "Photovoltaik [MWh]", "Sonstige Erneuerbare [MWh]"]
KONVENTIONELL = ["Braunkohle [MWh]", "Steinkohle [MWh]", "Erdgas [MWh]", "Kernenergie [MWh]", "Sonstige Konventionelle [MWh]"]

ERZEUGUNG_FILE = "Realisierte_Erzeugung_2025.csv"
VERBRAUCH_FILE = "Realisierter_Stromverbrauch_2025.csv"

mpl.rcParams.update({
'figure.dpi': 150, 'axes.grid': True, 'grid.linestyle': '--',
'grid.alpha': 0.3, 'axes.edgecolor': 'black', 'axes.linewidth': 1.0,
'font.size': 20, 'font.family': 'serif', 'mathtext.fontset': 'stix',
'legend.frameon': False, 'xtick.direction': 'in', 'ytick.direction': 'in',
'xtick.minor.visible': False, 'ytick.minor.visible': True,
})

erzeugung_df = pd.read_csv(ERZEUGUNG_FILE, na_values=['-'])
verbrauch_df = pd.read_csv(VERBRAUCH_FILE, na_values=['-'])

erzeugung_df['Datum'] = pd.to_datetime(erzeugung_df['Datum von'], format='%d.%m.%Y %H:%M')
verbrauch_df['Datum'] = pd.to_datetime(verbrauch_df['Datum von'], format='%d.%m.%Y %H:%M')

for col in ERNEUERBARE + KONVENTIONELL:
    if col in erzeugung_df.columns:
        erzeugung_df[col] = pd.to_numeric(erzeugung_df[col], errors='coerce')

if LAST in verbrauch_df.columns:
    verbrauch_df[LAST] = pd.to_numeric(verbrauch_df[LAST], errors='coerce')

erzeugung_df["Erneuerbare Erzeugung [MWh]"] = erzeugung_df[ERNEUERBARE].sum(axis=1)
erzeugung_df["Konventionelle Erzeugung [MWh]"] = erzeugung_df[KONVENTIONELL].sum(axis=1)

last_2025 = verbrauch_df[LAST].sum()

erneuerbare_2025 = erzeugung_df["Erneuerbare Erzeugung [MWh]"].sum()

konventionelle_2025 = erzeugung_df["Konventionelle Erzeugung [MWh]"].sum()
print(f"Netzlast 2025: {last_2025} MWh")
print(f"Erneuerbare Erzeugung 2025: {erneuerbare_2025} MWh")

print(f"Konventionelle Erzeugung 2025: {konventionelle_2025} MWh")
differenz = last_2025 - (erneuerbare_2025 + konventionelle_2025)
print(f"Residuallast 2025: {differenz} MWh")
faktor = last_2025 / erneuerbare_2025
print(f"Faktor: {faktor}")

erzeugung_df["Skalierte Erneuerbare Erzeugung [MWh]"] = erzeugung_df["Erneuerbare Erzeugung [MWh]"] * faktor

erzeugung_df.set_index('Datum', inplace=True)
verbrauch_df.set_index('Datum', inplace=True)

daily_verbrauch = verbrauch_df[LAST].resample('D').sum()
daily_erzeugung = erzeugung_df["Skalierte Erneuerbare Erzeugung [MWh]"].resample('D').sum()

# Convert MWh to GWh for better visualization
daily_verbrauch = daily_verbrauch / 1000000
daily_erzeugung = daily_erzeugung / 1000000

daily_residuallast = daily_verbrauch - daily_erzeugung

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

fig, ax = plt.subplots(figsize=(15, 6))

start_date = pd.to_datetime("2025-01-01")
end_date = pd.to_datetime("2025-12-31")
ax.set_xlim(start_date, end_date)

# Only use german month names for x-axis labels
monate = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
ax.set_xticks(pd.date_range(start_date, end_date, freq='MS'))
ax.set_xticklabels(monate)

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x:.1f}'.replace('.', ',')))

# Make the y = 0 line more visible
ax.axhline(0, color='black', linewidth=0.8, linestyle='--')

# ax.plot(daily_verbrauch.index, daily_verbrauch, label='Netzlast', color='orange', linewidth=1.8)
# ax.plot(daily_erzeugung.index, daily_erzeugung, label='Skalierte Erneuerbare Erzeugung', color='green', linewidth=1.8)
ax.plot(daily_residuallast.index, daily_residuallast, color='red', linewidth=1.8)


ax.set_xlabel("Datum")
ax.set_ylabel("Energie [TWh]")
ax.set_title("Tägliche Residualenergie im Jahr 2025")
ax.legend()
plt.tight_layout()
plt.show()

