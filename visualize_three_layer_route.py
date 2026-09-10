import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path


print("=" * 65)
print(" LUNAR CODEX - FINAL THREE-LAYER ROUTE VISUALIZATION")
print("=" * 65)


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

ICE_FILE = DATA_DIR / "sh_20230526.nc"
WIND_FILE = DATA_DIR / "aligned_wind_20230526.npy"
HAZARD_FILE = DATA_DIR / "hazard_risk_20230526.npy"
ROUTE_FILE = DATA_DIR / "three_layer_route_20230526.npy"

OUTPUT_FILE = DATA_DIR / "lunar_codex_final_route.png"


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

print("\nLoading environmental data...")

ds = xr.open_dataset(ICE_FILE)
ice = ds["tc_mid"].values[0]

wind = np.load(WIND_FILE)
hazard = np.load(HAZARD_FILE)
route = np.load(ROUTE_FILE)

print("✓ Ice loaded")
print("✓ Weather loaded")
print("✓ Hazard loaded")
print("✓ Route loaded")


# ------------------------------------------------------------
# ICE RISK
# ------------------------------------------------------------

ice_risk = np.full(
    ice.shape,
    np.nan,
    dtype=np.float32
)

mask = (ice >= 0) & (ice <= 100)
ice_risk[mask] = ice[mask]

ice_risk[ice == 110] = 100
ice_risk[ice == 118] = 0
ice_risk[ice == 119] = np.nan


# ------------------------------------------------------------
# WEATHER RISK
# ------------------------------------------------------------

weather_risk = np.full(
    wind.shape,
    np.nan,
    dtype=np.float32
)

mask = wind < 5
weather_risk[mask] = (wind[mask] / 5) * 20

mask = (wind >= 5) & (wind < 10)
weather_risk[mask] = (
    20 + ((wind[mask] - 5) / 5) * 20
)

mask = (wind >= 10) & (wind < 15)
weather_risk[mask] = (
    40 + ((wind[mask] - 10) / 5) * 30
)

mask = wind >= 15
weather_risk[mask] = 100


# ------------------------------------------------------------
# THREE-LAYER TOTAL RISK
# ------------------------------------------------------------

total_risk = (
    0.40 * ice_risk
    + 0.30 * weather_risk
    + 0.30 * hazard
)


# ------------------------------------------------------------
# ROUTE STATISTICS
# ------------------------------------------------------------

route_risks = np.array([
    total_risk[r, c]
    for r, c in route
])

print("\nRoute cells:", len(route))
print("Average risk:", f"{np.mean(route_risks):.2f}")
print("Maximum risk:", f"{np.max(route_risks):.2f}")


# ------------------------------------------------------------
# VISUALIZATION
# ------------------------------------------------------------

print("\nCreating final visualization...")

plt.figure(figsize=(14, 10))

image = plt.imshow(
    total_risk,
    cmap="turbo",
    vmin=0,
    vmax=100
)

plt.colorbar(
    image,
    label="Environmental Risk (0–100)"
)


# ------------------------------------------------------------
# ROUTE
# ------------------------------------------------------------

plt.plot(
    route[:, 1],
    route[:, 0],
    linewidth=2.5,
    label="Optimized A* Route"
)


# ------------------------------------------------------------
# START
# ------------------------------------------------------------

start = route[0]

plt.scatter(
    start[1],
    start[0],
    s=180,
    marker="*",
    edgecolors="black",
    linewidths=1.5,
    label="START",
    zorder=5
)


# ------------------------------------------------------------
# DESTINATION
# ------------------------------------------------------------

destination = route[-1]

plt.scatter(
    destination[1],
    destination[0],
    s=180,
    marker="X",
    edgecolors="black",
    linewidths=1.5,
    label="DESTINATION",
    zorder=5
)


# ------------------------------------------------------------
# TITLE
# ------------------------------------------------------------

plt.title(
    "LUNAR CODEX — AI Optimized Antarctic Navigation Route",
    fontsize=16,
    fontweight="bold"
)

plt.xlabel("Grid Column")
plt.ylabel("Grid Row")

plt.legend()

plt.grid(
    alpha=0.15
)

plt.tight_layout()


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

print("\n✓ FINAL MAP SAVED:")
print(OUTPUT_FILE)

plt.show()

print("\n" + "=" * 65)
print(" FINAL VISUALIZATION COMPLETE 🚀")
print("=" * 65)