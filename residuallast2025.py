import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

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
    'font.size': 16, 'font.family': 'serif', 'mathtext.fontset': 'stix',
    'legend.frameon': False, 'xtick.direction': 'in', 'ytick.direction': 'in',
    'xtick.minor.visible': True, 'ytick.minor.visible': True,
})



# CSV Einlesen
erzeugung_df = pd.read_csv(ERZEUGUNG_FILE, na_values=['-'])
verbrauch_df = pd.read_csv(VERBRAUCH_FILE, na_values=['-'])

# Convert columns to numeric, coercing errors
for col in ERNEUERBARE + KONVENTIONELL:
    if col in erzeugung_df.columns:
        erzeugung_df[col] = pd.to_numeric(erzeugung_df[col], errors='coerce')

if LAST in verbrauch_df.columns:
    verbrauch_df[LAST] = pd.to_numeric(verbrauch_df[LAST], errors='coerce')


# Energiekategorien summieren
erzeugung_df["Erneuerbare Erzeugung [MWh]"] = erzeugung_df[ERNEUERBARE].sum(axis=1)
erzeugung_df["Konventionelle Erzeugung [MWh]"] = erzeugung_df[KONVENTIONELL].sum(axis=1)

# Lastenergie für 2025 berechnen
last_2025 = verbrauch_df[LAST].sum()

# Erneuerbare und konventionelle Erzeugung für 2025 berechnen
erneuerbare_2025 = erzeugung_df["Erneuerbare Erzeugung [MWh]"].sum()
# konventionelle_2025 = erzeugung_df["Konventionelle Erzeugung [MWh]"].sum()

print(f"Netzlast 2025: {last_2025} MWh")
print(f"Erneuerbare Erzeugung 2025: {erneuerbare_2025} MWh")
# print(f"Konventionelle Erzeugung 2025: {konventionelle_2025} MWh")

# differenz = last_2025 - (erneuerbare_2025 + konventionelle_2025)
# print(f"Residuallast 2025: {differenz} MWh")

faktor = last_2025 / erneuerbare_2025
print(f"Faktor: {faktor}")

erzeugung_df["Skalierte Erneuerbare Erzeugung [MWh]"] = erzeugung_df["Erneuerbare Erzeugung [MWh]"] * faktor



# Convert 'Datum von' to datetime for plotting
erzeugung_df['Datum'] = pd.to_datetime(erzeugung_df['Datum von'], format='%d.%m.%Y %H:%M')
verbrauch_df['Datum'] = pd.to_datetime(verbrauch_df['Datum von'], format='%d.%m.%Y %H:%M')

plt.figure(figsize=(15, 8))

# Start- und Endzeitpunkt der x-Achse setzen
start_date = pd.to_datetime("2025-06-01")
end_date = pd.to_datetime("2025-06-30")
plt.xlim(start_date, end_date)

# Farben und Linienbreiten anpassen
plt.plot(verbrauch_df['Datum'], verbrauch_df[LAST], label='Netzlast', color='orange', linewidth=1.5)
plt.plot(erzeugung_df['Datum'], erzeugung_df["Skalierte Erneuerbare Erzeugung [MWh]"], label='Skalierte Erneuerbare Erzeugung', color='green', linewidth=1.5)

plt.xlabel("Datum")
plt.ylabel("Energie [MWh]")
plt.title("Netzlast und Skalierte Erneuerbare Erzeugung in 2025")
plt.legend()
plt.show()