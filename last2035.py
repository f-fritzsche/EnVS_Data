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


# Importiere die Daten

FILE = "DE00_Demand_total_2035_National Trends.csv"

dataframe = pd.read_csv(FILE)

# Drop "month", "day", "hour" columns
dataframe.drop(columns=["Month", "Day", "Hour"], inplace=True)

# Reformat "date" column to datetime
dataframe["Date"] = pd.to_datetime(dataframe["Date"])

# For every column except the first one, sum all rows and print the result
sums = []

for column in dataframe.columns[1:]:
    total = dataframe[column].sum()
    # Save the total to an array for later use
    sums.append(total)

# Calculate max, min, and average of the sums
max_sum = max(sums)
min_sum = min(sums)
avg_sum = sum(sums) / len(sums)

# Get the name of the column with the max sum
max_column = dataframe.columns[1:][sums.index(max_sum)]
min_column = dataframe.columns[1:][sums.index(min_sum)]

# Get the column closest to the average sum
closest_column = dataframe.columns[1:][min(range(len(sums)), key=lambda i: abs(sums[i] - avg_sum))]

print(f"Max: {max_column} with {max_sum} MWh")
print(f"Min: {min_column} with {min_sum} MWh")
print(f"Average: {avg_sum} MWh, closest column: {closest_column}")

# create a new dataframe with the columns "Date", "Max", "Min", "Average"
new_dataframe = pd.DataFrame({
    "Date": dataframe["Date"],
    "Max": dataframe[max_column],
    "Min": dataframe[min_column],
    "Average": dataframe[closest_column]
})

print(new_dataframe.head())

new_dataframe.set_index("Date", inplace=True)

daily_max = new_dataframe["Max"].resample('D').sum()
daily_min = new_dataframe["Min"].resample('D').sum()
daily_avg = new_dataframe["Average"].resample('D').sum()

# convert to TWh for better visualization
daily_max = daily_max / 1000000
daily_min = daily_min / 1000000
daily_avg = daily_avg / 1000000

# plot the daily values
fig, ax = plt.subplots(figsize=(15, 6))

start_date = pd.to_datetime("2018-01-01")
end_date = pd.to_datetime("2018-12-31")
ax.set_xlim(start_date, end_date)

# Only use german month names for x-axis labels
monate = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
ax.set_xticks(pd.date_range(start_date, end_date, freq='MS'))
ax.set_xticklabels(monate)

ax.plot(daily_max.index, daily_max, label=f"Max ({max_column})", color="red", linewidth=1.8)
ax.plot(daily_min.index, daily_min, label=f"Min ({min_column})", color="blue", linewidth=1.8)
ax.plot(daily_avg.index, daily_avg, label=f"Ø ({closest_column})", color="green", linewidth=1.8)
ax.set_xlabel("Datum")
ax.set_ylabel("Energie [TWh]")
ax.set_title("Tägliche Netzlast im Jahr 2035")
ax.legend()
plt.tight_layout()
plt.show()

# Calculate the year-total for the max, min, and average columns
year_total_max = daily_max.sum()
year_total_min = daily_min.sum()
year_total_avg = daily_avg.sum()

print(f"Year total Max: {year_total_max} TWh")
print(f"Year total Min: {year_total_min} TWh")
print(f"Year total Average: {year_total_avg} TWh")

# Export the hourly average column to a new CSV file with the columns "Date" and "Load"
export_df = new_dataframe[["Average"]].reset_index()
export_df.rename(columns={"Average": "Load"}, inplace=True)
export_df.to_csv("average_load_2035.csv", index=False)