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

PUFFER_GWH = 0 #10960

WIRKUNGSGRAD_EINSPEICHERUNG = 0.8
WIRKUNGSGRAD_AUSSPREICHERUNG = 0.55


# ==========================================
# 1. Daten einlesen & Vorbereiten
# ==========================================
df = pd.read_csv('residuallast_2035.csv') 
residuallast = df['Residuallast'].values

residuallast_gw = residuallast / 1000  # von MW auf GW
# ==========================================


# Definition der Leistungsflüsse aus Sicht des Speichers:
# Residuallast > 0 (Defizit) -> Speicher muss entladen (negativer Wert für Speicher)
# Residuallast < 0 (Überschuss) -> Speicher kann laden (positiver Wert für Speicher)
speicher_fluss_gwh = -residuallast_gw 

# ==========================================
# 2. Lade- und Entladeleistung bestimmen
# ==========================================
# Die maximale Leistung in GW entspricht dem maximalen stündlichen Energiefluss in GWh/h
max_ladeleistung_gw = max(0, speicher_fluss_gwh.max())
max_entladeleistung_gw = max(0, -speicher_fluss_gwh.min())

print(f"--- BENÖTIGTE LEISTUNGEN ---")
print(f"Maximale Ladeleistung (z.B. Elektrolyseur):   {max_ladeleistung_gw:.2f} GW")
print(f"Maximale Entladeleistung (z.B. Gasturbine):   {max_entladeleistung_gw:.2f} GW\n")

# ==========================================
# 3. Notwendige Kapazität berechnen (Maximum Drawdown über 2 Jahre)
# ==========================================
# Wir hängen die Zeitreihe des Jahres zweimal aneinander (Periodizität),
# um saisonale Zyklen zu erfassen, die über den Jahreswechsel hinausgehen.
speicher_fluss_2_jahre = np.tile(speicher_fluss_gwh, 2)

# Wir simulieren die kumulierte Summe nun über 17.520 Stunden (2 Jahre)
kumulierte_energie = np.cumsum(np.insert(speicher_fluss_2_jahre, 0, 0))

# Wir ermitteln für jeden Zeitpunkt den bisherigen historischen Höchststand
bisheriges_maximum = np.maximum.accumulate(kumulierte_energie)

# Der Drawdown ist der Abfall vom Höchststand.
# Durch die 2 Jahre wird nun auch ein Zyklus von z.B. Oktober (Jahr 1) bis März (Jahr 2) korrekt erfasst!
drawdowns = bisheriges_maximum - kumulierte_energie
kapazitaet_gwh = drawdowns.max()
kapazitaet_twh = kapazitaet_gwh / 1000

print(f"--- SPEICHERKAPAZITÄT ---")
print(f"Benötigte nutzbare Speicherkapazität (aus 2-Jahres-Zyklus): {kapazitaet_twh:.2f} TWh\n")


# ==========================================
# 4. Zeitreihen-Simulation (Der reale Füllstand)
# ==========================================
# Jetzt simulieren wir den Speicher chronologisch mit harten Grenzen (0 und Max-Kapazität).
# Für die Berechnung nehmen wir an, der Speicher startet am 1. Januar voll.

minimum_soc = []
minimum_soc.append(0) # Start mit leerem Speicher, damit die Simulation nicht sofort mit einem Defizit startet, das nicht durch den Speicher ausgeglichen werden kann.

for l in range(10):
    soc_gwh = np.zeros(len(residuallast_gw))
    aktueller_soc = kapazitaet_gwh
    #sum all minimum socs and subtract from aktueller_soc to simulate the drawdown of the storage over the years
    minimum_soc_sum = sum(minimum_soc)
    aktueller_soc -= minimum_soc_sum

    abgeregelte_energie_gwh = 0

    for i, fluss in enumerate(speicher_fluss_gwh):
        neuer_soc = aktueller_soc + fluss
        
        # KAPPUNG OBEN (Speicher ist voll -> Überschuss wird abgeregelt/verfällt)
        if neuer_soc > kapazitaet_gwh:
            abgeregelte_energie_gwh += (neuer_soc - kapazitaet_gwh)
            aktueller_soc = kapazitaet_gwh
            
        # KAPPUNG UNTEN (Speicher ist leer -> Darf nicht unter 0 fallen)
        # (Sollte bei korrekter Drawdown-Berechnung genau 1x bei 0 ankommen, aber nie darunter)
        elif neuer_soc < 0:
            aktueller_soc = 0
            print(f"Warnung: Speicherfüllstand ist unter 0 gefallen! Das sollte mit der Drawdown-Berechnung nicht passieren. Neuer Füllstand wurde auf 0 gesetzt.")
            
        else:
            aktueller_soc = neuer_soc
            
        soc_gwh[i] = aktueller_soc

    print(f"--- SYSTEMBILANZ ---")
    print(f"Ungenutzte (abgeregelte) Überschussenergie:     {abgeregelte_energie_gwh / 1000:.2f} TWh")
    print(f"Speicherfüllstand am Jahresende:                {soc_gwh[-1] / 1000:.2f} TWh")
    if soc_gwh.min() > 0:
        print(f"Minimum Füllstand:                              {soc_gwh.min()} GWh")
        minimum_soc.append(soc_gwh.min())
    else: break

# Neuberechnung der tatsächlichen Lade- und Entladeleistung, da durch die Simulation mit harten Grenzen die tatsächlichen Flüsse abweichen können.
tatsache_ladeleistung_gw = max(0, (soc_gwh - np.insert(soc_gwh[:-1], 0, kapazitaet_gwh)).max())
tatsache_entladeleistung_gw = min(0, (soc_gwh - np.insert(soc_gwh[:-1], 0, kapazitaet_gwh)).min()) * -1

print(f"\n--- TATSÄCHLICHE LEISTUNGEN NACH SIMULATION ---")
print(f"Tatsächliche maximale Ladeleistung:   {tatsache_ladeleistung_gw:.2f} GW")
print(f"Tatsächliche maximale Entladeleistung: {tatsache_entladeleistung_gw:.2f} GW")

# ==========================================
# 5. Visualisierung
# ==========================================
plt.figure(figsize=(14, 7), dpi=150)

# Füllstand in TWh umrechnen für den Plot
soc_twh = soc_gwh / 1000

plt.plot(soc_twh, color='#2ca02c', linewidth=1.5, label='Speicherfüllstand')
plt.axhline(y=kapazitaet_twh, color='red', linestyle='--', linewidth=1, label=f'Kapazität ({kapazitaet_twh:.2f} TWh)')
plt.axhline(0, color='black', linewidth=0.8, linestyle='--')

# Optik anpassen
plt.title('Simulation des saisonalen Speicherfüllstands in der Prognose 2035', pad=15)
plt.ylabel('Füllstand [TWh]')
plt.xlim(0, 8760)
plt.ylim(-1, kapazitaet_twh * 1.1)

# X-Achse grob in Monate einteilen (8760 Stunden / 12)
monate = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
plt.xticks(np.linspace(0, 8760, 12, endpoint=False), monate)

plt.legend(loc='lower right')
plt.tight_layout()
plt.show()