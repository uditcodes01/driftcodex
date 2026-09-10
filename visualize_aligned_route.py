import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# LUNAR CODEX - RISK-BUFFERED ROUTE VISUALIZATION
# ============================================================

print("=" * 60)
print(" LUNAR CODEX - RISK-BUFFERED ROUTE VISUALIZATION")
print("=" * 60)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

ICE_FILE = DATA_DIR / "sh_20230526.nc"
WIND_FILE = DATA_DIR / "aligned_wind_20230526.npy"
ROUTE_FILE = DATA_DIR / "optimized_route.npy"


# ============================================================
# START / DESTINATION
# ============================================================

START = (402, 490)
DESTINATION = (501, 51)


# ============================================================
# CHECK FILES
# ============================================================

print("\nChecking files...")

for file in [ICE_FILE, WIND_FILE, ROUTE_FILE]:

    if not file.exists():
        raise FileNotFoundError(
            f"File not found:\n{file}"
        )

print("✓ Ice data found")
print("✓ Weather data found")
print("✓ Optimized route found")


# ============================================================
# LOAD ICE
# ============================================================

print("\nLoading ice data...")

ice_ds = xr.open_dataset(ICE_FILE)

ice_data = ice_ds["tc_mid"].values[0]


# ============================================================
# ICE RISK
# ============================================================

ice_risk = np.full(
    ice_data.shape,
    np.nan,
    dtype=np.float32
)

real_ice = (
    (ice_data >= 0)
    &
    (ice_data <= 100)
)

ice_risk[real_ice] = ice_data[real_ice]

ice_risk[ice_data == 110] = 100

ice_risk[ice_data == 118] = 0

ice_risk[ice_data == 119] = np.nan


# ============================================================
# LOAD WEATHER
# ============================================================

print("Loading weather data...")

wind_speed = np.load(WIND_FILE)


# ============================================================
# WEATHER RISK
# ============================================================

weather_risk = np.full(
    wind_speed.shape,
    np.nan,
    dtype=np.float32
)


# Wind < 5 m/s
mask = wind_speed < 5

weather_risk[mask] = (
    wind_speed[mask] / 5
) * 20


# Wind 5-10 m/s
mask = (
    (wind_speed >= 5)
    &
    (wind_speed < 10)
)

weather_risk[mask] = (
    20
    +
    ((wind_speed[mask] - 5) / 5) * 20
)


# Wind 10-15 m/s
mask = (
    (wind_speed >= 10)
    &
    (wind_speed < 15)
)

weather_risk[mask] = (
    40
    +
    ((wind_speed[mask] - 10) / 5) * 30
)


# Wind >= 15 m/s
mask = wind_speed >= 15

weather_risk[mask] = 100


# ============================================================
# COMBINED RISK
# ============================================================

combined_risk = (
    0.60 * ice_risk
    +
    0.40 * weather_risk
)

combined_risk[
    np.isnan(ice_risk)
] = np.nan


# ============================================================
# LOAD OPTIMIZED ROUTE
# ============================================================

print("Loading optimized route...")

route = np.load(
    ROUTE_FILE
)

route = [
    tuple(cell)
    for cell in route
]

print(
    f"Route cells: {len(route)}"
)


# ============================================================
# ROUTE RISK
# ============================================================

route_risks = np.array([
    combined_risk[r, c]
    for r, c in route
])


average_risk = np.mean(
    route_risks
)

maximum_risk = np.max(
    route_risks
)

safe_count = np.sum(
    route_risks < 30
)

caution_count = np.sum(
    (route_risks >= 30)
    &
    (route_risks < 60)
)

dangerous_count = np.sum(
    (route_risks >= 60)
    &
    (route_risks < 80)
)

critical_count = np.sum(
    route_risks >= 80
)


# ============================================================
# PRINT ROUTE RESULTS
# ============================================================

print("\n" + "=" * 60)
print(" OPTIMIZED ROUTE")
print("=" * 60)

print(
    f"\nAverage risk: {average_risk:.2f}"
)

print(
    f"Maximum risk: {maximum_risk:.2f}"
)

print(
    f"SAFE: {safe_count}"
)

print(
    f"CAUTION: {caution_count}"
)

print(
    f"DANGEROUS: {dangerous_count}"
)

print(
    f"CRITICAL: {critical_count}"
)


# ============================================================
# ROUTE COORDINATES
# ============================================================

route_rows = [
    cell[0]
    for cell in route
]

route_cols = [
    cell[1]
    for cell in route
]


# ============================================================
# CREATE FIGURE
# ============================================================

print("\nCreating visualization...")


plt.figure(
    figsize=(15, 10)
)


# ============================================================
# RISK MAP
# ============================================================

plt.imshow(
    combined_risk,
    origin="upper",
    interpolation="nearest"
)


# ============================================================
# ROUTE
# ============================================================

plt.plot(
    route_cols,
    route_rows,
    linewidth=2,
    label="Risk-Buffered A* Route"
)


# ============================================================
# START
# ============================================================

plt.scatter(
    START[1],
    START[0],
    s=180,
    marker="o",
    edgecolors="black",
    label="START",
    zorder=5
)


# ============================================================
# DESTINATION
# ============================================================

plt.scatter(
    DESTINATION[1],
    DESTINATION[0],
    s=220,
    marker="*",
    edgecolors="black",
    label="DESTINATION",
    zorder=5
)


# ============================================================
# LABELS
# ============================================================

plt.text(
    START[1] + 10,
    START[0],
    "START",
    fontsize=11,
    weight="bold"
)


plt.text(
    DESTINATION[1] + 10,
    DESTINATION[0],
    "DESTINATION",
    fontsize=11,
    weight="bold"
)


# ============================================================
# COLORBAR
# ============================================================

colorbar = plt.colorbar()

colorbar.set_label(
    "Combined Environmental Risk (0-100)"
)


# ============================================================
# TITLE
# ============================================================

plt.title(
    "LUNAR CODEX\n"
    "Risk-Buffered A* Antarctic Route Optimization",
    fontsize=17,
    weight="bold"
)


plt.xlabel(
    "Grid Column"
)

plt.ylabel(
    "Grid Row"
)


plt.legend()


plt.tight_layout()


# ============================================================
# SAVE IMAGE
# ============================================================

output_file = (
    DATA_DIR
    /
    "lunar_codex_risk_buffered_route.png"
)


plt.savefig(
    output_file,
    dpi=200,
    bbox_inches="tight"
)


print("\n✓ Visualization saved:")

print(
    output_file
)


# ============================================================
# SHOW
# ============================================================

print(
    "\nOpening visualization..."
)

plt.show()


print("\n" + "=" * 60)
print(" VISUALIZATION COMPLETE 🚀")
print("=" * 60)