import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams.update({
    'figure.dpi': 150, 'axes.grid': True, 'grid.linestyle': '--',
    'axes.grid.axis': 'y',
    'grid.alpha': 0.3, 'axes.edgecolor': 'black', 'axes.linewidth': 1.0,
    'font.size': 20, 'font.family': 'serif', 'mathtext.fontset': 'stix',
    'legend.frameon': False, 'xtick.direction': 'in', 'ytick.direction': 'in',
    'xtick.minor.visible': False, 'ytick.minor.visible': True,
})

PUFFER_GWH = 5000

WIRKUNGSGRAD_EINSPEICHERUNG = 0.8 * 0.99
WIRKUNGSGRAD_AUSSPEICHERUNG = 0.55 * 0.99

ws = ["WS01", "WS02", "WS03", "WS04", "WS05", "WS06", "WS07", "WS08", "WS09", "WS10",
      "WS11", "WS12", "WS13", "WS14", "WS15", "WS16", "WS17", "WS18", "WS19", "WS20",
      "WS21", "WS22", "WS23", "WS24", "WS25", "WS26", "WS27", "WS28", "WS29", "WS30",
      "WS31", "WS32", "WS33", "WS34", "WS35", "WS36"]

# Stat tracking
overall_surplus = []
storage_needed_list = []

# ==========================================
# 1. Daten einlesen & Vorbereiten
# ==========================================

df = pd.read_csv('output/residuallast_2035_all_ws.csv') 

for w in ws:
    residuallast = df[w].values
    residuallast_gw = residuallast / 1000  # von MW auf GW


    # Definition der Leistungsflüsse aus Sicht des Speichers:
    # Residuallast > 0 (Defizit) -> Speicher muss entladen (negativer Wert für Speicher)
    # Residuallast < 0 (Überschuss) -> Speicher kann laden (positiver Wert für Speicher)
    speicher_fluss_unbereinigt_gwh = -residuallast_gw 

    for i in range(len(speicher_fluss_unbereinigt_gwh)):
        if speicher_fluss_unbereinigt_gwh[i] > 0: # Ladephase
            speicher_fluss_unbereinigt_gwh[i] *= WIRKUNGSGRAD_EINSPEICHERUNG
        else: # Entladephase
            speicher_fluss_unbereinigt_gwh[i] /= WIRKUNGSGRAD_AUSSPEICHERUNG

    speicher_fluss_gwh =speicher_fluss_unbereinigt_gwh.copy()

    # ==========================================
    # 2. Lade- und Entladeleistung bestimmen
    # ==========================================

    max_ladeleistung_gw = max(0, speicher_fluss_gwh.max())
    max_entladeleistung_gw = max(0, -speicher_fluss_gwh.min())

    print(f"--- BENÖTIGTE LEISTUNGEN ---")
    print(f"Maximale Ladeleistung (z.B. Elektrolyseur):   {max_ladeleistung_gw:.2f} GW")
    print(f"Maximale Entladeleistung (z.B. Gasturbine):   {max_entladeleistung_gw:.2f} GW\n")

    # ==========================================
    # 3. Notwendige Kapazität berechnen 
    # ==========================================

    speicher_fluss_2_jahre = np.tile(speicher_fluss_gwh, 2)

    # Wir simulieren die kumulierte Summe nun über 17.520 Stunden (2 Jahre)
    kumulierte_energie = np.cumsum(np.insert(speicher_fluss_2_jahre, 0, 0))

    # Wir ermitteln für jeden Zeitpunkt den bisherigen historischen Höchststand
    bisheriges_maximum = np.maximum.accumulate(kumulierte_energie)

    # Der Drawdown ist der Abfall vom Höchststand.
    drawdowns = bisheriges_maximum - kumulierte_energie
    kapazitaet_gwh = drawdowns.max()
    kapazitaet_twh = kapazitaet_gwh / 1000

    print(f"--- SPEICHERKAPAZITÄT ---")
    print(f"Benötigte nutzbare Speicherkapazität (aus 2-Jahres-Zyklus): {kapazitaet_twh:.2f} TWh\n")

    storage_needed_list.append(kapazitaet_gwh)

    # Calculate the totals directly from the array that the simulation is about to use
    eff_in_twh = speicher_fluss_gwh[speicher_fluss_gwh > 0].sum() / 1000
    eff_out_twh = speicher_fluss_gwh[speicher_fluss_gwh < 0].sum() / 1000
    net_change_twh = speicher_fluss_gwh.sum() / 1000

    print(f"--- BEREINIGTE SPEICHERFLÜSSE ---")
    print(f"Effective Energy IN :       {eff_in_twh:.2f} TWh")
    print(f"Effective Energy OUT:       {eff_out_twh:.2f} TWh")
    print(f"Net Change in Storage:      {net_change_twh:.2f} TWh\n")

    overall_surplus.append(net_change_twh)

    # ==========================================
    # 4. Zeitreihen-Simulation 
    # ==========================================


    c_puffer = 0.1*kapazitaet_gwh
    c_puffer = 0
    kapazitaet_gwh += c_puffer

    minimum_soc = []
    minimum_soc.append(0) 

    for l in range(10):
        soc_gwh = np.zeros(len(residuallast_gw))
        aktueller_soc = kapazitaet_gwh
        minimum_soc_sum = sum(minimum_soc)
        aktueller_soc -= minimum_soc_sum

        print(f"--- SIMULATION DURCHLAUF {l+1} ---")
        print(f"Start Füllstand:                                {aktueller_soc / 1000:.2f} TWh")

        abgeregelte_energie_gwh = 0

        for i, fluss in enumerate(speicher_fluss_gwh):

            neuer_soc = aktueller_soc + fluss
            
            # KAPPUNG OBEN (Speicher ist voll -> Überschuss wird abgeregelt/verfällt)
            if neuer_soc > kapazitaet_gwh:
                abgeregelte_energie_gwh += (neuer_soc - kapazitaet_gwh)
                aktueller_soc = kapazitaet_gwh
                
            # KAPPUNG UNTEN (Speicher ist leer -> Darf nicht unter 0 fallen)
            elif neuer_soc < 0:
                aktueller_soc = 0
                print(f"WARNING")
                
            else:
                aktueller_soc = neuer_soc

            soc_gwh[i] = aktueller_soc

        print(f"Ungenutzte (abgeregelte) Überschussenergie:     {abgeregelte_energie_gwh / 1000:.2f} TWh")
        print(f"Speicherfüllstand am Jahresende:                {soc_gwh[-1] / 1000:.2f} TWh")
        if soc_gwh.min() > c_puffer:
            print(f"Minimum Füllstand:                              {soc_gwh.min()} GWh")
            minimum_soc.append(soc_gwh.min()-c_puffer)
        else: break

    # Neuberechnung der tatsächlichen Lade- und Entladeleistung, da durch die Simulation mit harten Grenzen die tatsächlichen Flüsse abweichen können
    tatsache_ladeleistung_gw = max(0, np.max(np.diff(soc_gwh)))
    tatsache_entladeleistung_gw = max(0, -np.min(np.diff(soc_gwh)))


    print(f"\n--- TATSÄCHLICHE LEISTUNGEN NACH SIMULATION ---")
    print(f"Tatsächliche maximale Ladeleistung:   {tatsache_ladeleistung_gw:.2f} GW")
    print(f"Tatsächliche maximale Entladeleistung: {tatsache_entladeleistung_gw:.2f} GW")

    # ==========================================
    # 5. Visualisierung
    # ==========================================

    # plt.figure(figsize=(14, 7), dpi=150)

    # # Füllstand in TWh umrechnen für den Plot
    # soc_twh = soc_gwh / 1000

    # plt.plot(soc_twh, color='#2ca02c', linewidth=1.5, label='Speicherfüllstand')
    # plt.axhline(y=kapazitaet_twh, color='red', linestyle='--', linewidth=1, label=f'Kapazität ({kapazitaet_twh:.2f} TWh)')
    # plt.axhline(0, color='black', linewidth=0.8, linestyle='--')

    # # Optik anpassen
    # plt.title(f'Simulation des saisonalen Speicherfüllstands in der Prognose 2035 - {w}', pad=15)
    # plt.ylabel('Füllstand [TWh]')
    # plt.xlim(0, 8760)
    # plt.ylim(-1, kapazitaet_twh * 1.1)

    # # X-Achse grob in Monate einteilen (8760 Stunden / 12)
    # monate = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
    # plt.xticks(np.linspace(0, 8760, 12, endpoint=False), monate)

    # plt.legend(loc='lower right')
    # plt.tight_layout()
    # plt.show()

average_storage_needed = np.mean(storage_needed_list)
max_storage_needed = np.max(storage_needed_list)
min_storage_needed = np.min(storage_needed_list)
median_storage_needed = np.median(storage_needed_list)

print(f"\n--- ÜBERGREIFENDER STATISTIK ---")
print(f"Anzahl der WS mit positivem Netto-Speicherfluss:        {sum(1 for x in overall_surplus if x > 0)} von {len(ws)}")
print(f"Maximal benötigte nutzbare Speicherkapazität:           {max_storage_needed / 1000:.2f} TWh")
print(f"Minimal benötigte nutzbare Speicherkapazität:           {min_storage_needed / 1000:.2f} TWh")
print(f"Durchschnittlich benötigte nutzbare Speicherkapazität:  {average_storage_needed / 1000:.2f} TWh")
print(f"Median benötigte nutzbare Speicherkapazität:            {median_storage_needed / 1000:.2f} TWh")

avg_s = average_storage_needed/1000
avg_s = round(avg_s, 2)
avg_s = avg_s.__str__()
# replace dot with comma for german formatting
avg_s = avg_s.replace('.', ',')

# Plot der Verteilung der benötigten Speicherkapazitäten über die 36 WS (x-Achse WS, y-Achse benötigte Kapazität in TWh)
plt.figure(figsize=(12, 6))
bar_colors = ['green' if is_surplus > 0 else 'red' for is_surplus in overall_surplus]
plt.bar(ws, np.array(storage_needed_list) / 1000, color=bar_colors)
plt.axhline(average_storage_needed / 1000, color='blue', linestyle='--', label=f'Ø {avg_s} TWh')
plt.title('Benötigte Speicherkapazität über alle Wetterszenarien', pad=15)
plt.ylabel('Speicherkapazität [TWh]')
plt.xticks(rotation=90)
plt.legend()
plt.tight_layout()
plt.show()

# Plot des overall_surplus (Netto-Speicherfluss) über die 36 WS (x-Achse WS, y-Achse Netto-Speicherfluss in TWh)
plt.figure(figsize=(12, 6))
plt.bar(ws, np.array(overall_surplus), color=bar_colors)
plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
plt.title('Netto-Energiebilanz über alle Wetterszenarien', pad=15)
plt.ylabel('Netto-Energiebilanz [TWh]')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()