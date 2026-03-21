import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams.update({
    'figure.dpi': 150, 'axes.grid': True, 'grid.linestyle': '--',
    'grid.alpha': 0.3, 'axes.edgecolor': 'black', 'axes.linewidth': 1.0,
    'font.size': 20, 'font.family': 'serif', 'mathtext.fontset': 'stix',
    'legend.frameon': False, 'xtick.direction': 'in', 'ytick.direction': 'in',
    'xtick.minor.visible': False, 'ytick.minor.visible': True,
})

# ==========================================
# 1. Daten einlesen
# ==========================================
# Ersetze 'deine_rohdaten.csv' mit deinem Dateinamen
# Wir nehmen an, die Spalte mit der Residuallast in GW heißt 'Residuallast_GW'
df = pd.read_csv('residuallast_2035.csv') 
residuallast = df['Residuallast'].values

residuallast = residuallast / 1000  # von MW auf GW

# ==========================================
# 2. Benötigte Leistungen bestimmen
# ==========================================
# Negative Werte = Einspeichern (Laden)
# Positive Werte = Ausspeichern (Entladen)
max_ladeleistung = abs(residuallast.min()) 
max_entladeleistung = residuallast.max()

print(f"Maximale Ladeleistung (Elektrolyse/Pumpe):   {max_ladeleistung:.2f} GW")
print(f"Maximale Entladeleistung (Brennstoffzelle/Turbine): {max_entladeleistung:.2f} GW")
print("-" * 50)

# ==========================================
# 3. Zeitreihensimulation des Speichers
# ==========================================
# Vorbereitung für deinen späteren Technologievergleich:
eta_in = 1.0   # Wirkungsgrad Einspeichern (z.B. später 0.65 für Elektrolyse)
eta_out = 1.0  # Wirkungsgrad Ausspeichern (z.B. später 0.50 für Brennstoffzelle)

soc = np.zeros(len(residuallast)) # SOC = State of Charge (Füllstand in GWh)
aktueller_fuellstand = 0.0

for i, r in enumerate(residuallast):
    if r > 0:
        # Defizit: Wir müssen den Speicher entladen.
        # Bei Wirkungsgrad < 1 verliert man hier Energie, man muss also MEHR aus dem Speicher ziehen!
        aktueller_fuellstand -= (r / eta_out)
    else:
        # Überschuss: Wir laden den Speicher.
        # Bei Wirkungsgrad < 1 kommt nur ein Teil der Energie im Speicher an!
        # (Da r negativ ist, rechnen wir Minus mal Plus = Minus, aber wir ziehen es ab, also wächst der Füllstand)
        aktueller_fuellstand -= (r * eta_in)
    
    soc[i] = aktueller_fuellstand

# ==========================================
# 4. Speicherkapazität berechnen
# ==========================================
# Die benötigte Kapazität ist die Differenz zwischen dem Maximum und Minimum der simulierten Kurve.
benoetigte_kapazitaet_gwh = soc.max() - soc.min()
benoetigte_kapazitaet_twh = benoetigte_kapazitaet_gwh / 1000

print(f"Benötigte nutzbare Speicherkapazität: {benoetigte_kapazitaet_twh:.2f} TWh")

# ==========================================
# 5. Visualisierung (Optional)
# ==========================================
# Damit der Graph Sinn macht, verschieben wir die Füllstandskurve so nach oben, 
# dass der tiefste Punkt im Jahr genau bei 0 TWh liegt (komplett leerer Speicher).
soc_real_twh = (soc - soc.min()) / 1000

plt.figure(figsize=(12, 6), dpi=150)
plt.plot(soc_real_twh, color='blue', linewidth=1.5)
plt.title(f'Saisonaler Speicherfüllstand im Jahr 2025\n(Idealfall: 100% Wirkungsgrad, Kapazität: {benoetigte_kapazitaet_twh:.2f} TWh)')
plt.xlabel('Stunden im Jahr')
plt.ylabel('Füllstand [TWh]')
plt.grid(True, linestyle=':', alpha=0.7)
plt.xlim(0, len(soc))
plt.ylim(0, benoetigte_kapazitaet_twh * 1.05)
plt.show()