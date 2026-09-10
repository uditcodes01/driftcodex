import numpy as np
import xarray as xr
from pathlib import Path


print("=" * 65)
print(" LUNAR CODEX - THREE-LAYER ENVIRONMENTAL RISK MODEL")
print("=" * 65)


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

ICE_FILE = DATA_DIR / "sh_20230526.nc"
WIND_FILE = DATA_DIR / "aligned_wind_20230526.npy"
HAZARD_FILE = DATA_DIR / "hazard_risk_20230526.npy"

OUTPUT_FILE = DATA_DIR / "total_risk_20230526.npy"


# ------------------------------------------------------------
# CHECK FILES
# ------------------------------------------------------------

print("\nChecking data files...")

for file in [
    ICE_FILE,
    WIND_FILE,
    HAZARD_FILE
]:

    if not file.exists():

        raise FileNotFoundError(
            f"Missing file:\n{file}"
        )

print("✓ USNIC sea-ice data found")
print("✓ ERA5 aligned weather data found")
print("✓ Iceberg hazard data found")


# ------------------------------------------------------------
# LOAD ICE DATA
# ------------------------------------------------------------

print("\nLoading sea-ice data...")

ice_ds = xr.open_dataset(
    ICE_FILE
)

ice_data = ice_ds[
    "tc_mid"
].values[0]


# ------------------------------------------------------------
# CONVERT ICE TO RISK
# ------------------------------------------------------------

ice_risk = np.full(
    ice_data.shape,
    np.nan,
    dtype=np.float32
)


# Normal ice concentration

mask = (
    (ice_data >= 0)
    &
    (ice_data <= 100)
)

ice_risk[mask] = (
    ice_data[mask]
)


# Fast ice

ice_risk[
    ice_data == 110
] = 100


# Usually ocean

ice_risk[
    ice_data == 118
] = 0


# Land

ice_risk[
    ice_data == 119
] = np.nan


# ------------------------------------------------------------
# LOAD WEATHER
# ------------------------------------------------------------

print("Loading aligned weather data...")

wind_speed = np.load(
    WIND_FILE
)


print(
    f"Weather grid: {wind_speed.shape}"
)


# ------------------------------------------------------------
# WEATHER RISK
# ------------------------------------------------------------

print("\nCalculating weather risk...")


weather_risk = np.full(
    wind_speed.shape,
    np.nan,
    dtype=np.float32
)


# 0–5 m/s → 0–20

mask = wind_speed < 5

weather_risk[mask] = (
    wind_speed[mask]
    /
    5
) * 20


# 5–10 m/s → 20–40

mask = (
    (wind_speed >= 5)
    &
    (wind_speed < 10)
)

weather_risk[mask] = (
    20
    +
    (
        (wind_speed[mask] - 5)
        /
        5
    ) * 20
)


# 10–15 m/s → 40–70

mask = (
    (wind_speed >= 10)
    &
    (wind_speed < 15)
)

weather_risk[mask] = (
    40
    +
    (
        (wind_speed[mask] - 10)
        /
        5
    ) * 30
)


# >15 m/s → critical

mask = wind_speed >= 15

weather_risk[mask] = 100


# ------------------------------------------------------------
# LOAD ICEBERG HAZARD
# ------------------------------------------------------------

print("Loading iceberg hazard layer...")

hazard_risk = np.load(
    HAZARD_FILE
)


print(
    f"Hazard grid: {hazard_risk.shape}"
)


# ------------------------------------------------------------
# VERIFY GRID ALIGNMENT
# ------------------------------------------------------------

print("\nChecking grid alignment...")


if not (
    ice_risk.shape
    ==
    weather_risk.shape
    ==
    hazard_risk.shape
):

    raise ValueError(
        "Environmental grids do not match!"
    )


print(
    f"✓ All grids match: "
    f"{ice_risk.shape}"
)


# ------------------------------------------------------------
# TOTAL RISK
# ------------------------------------------------------------

print("\nCalculating total environmental risk...")


# Final SIH model

ICE_WEIGHT = 0.40
WEATHER_WEIGHT = 0.30
HAZARD_WEIGHT = 0.30


print("\nRisk weights:")

print(
    f"Ice:     {ICE_WEIGHT * 100:.0f}%"
)

print(
    f"Weather: {WEATHER_WEIGHT * 100:.0f}%"
)

print(
    f"Hazard:  {HAZARD_WEIGHT * 100:.0f}%"
)


# Valid cells

valid = (
    ~np.isnan(ice_risk)
    &
    ~np.isnan(weather_risk)
    &
    ~np.isnan(hazard_risk)
)


total_risk = np.full(
    ice_risk.shape,
    np.nan,
    dtype=np.float32
)


total_risk[valid] = (
    ICE_WEIGHT * ice_risk[valid]
    +
    WEATHER_WEIGHT * weather_risk[valid]
    +
    HAZARD_WEIGHT * hazard_risk[valid]
)


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

np.save(
    OUTPUT_FILE,
    total_risk
)


# ------------------------------------------------------------
# STATISTICS
# ------------------------------------------------------------

valid_risk = total_risk[
    ~np.isnan(total_risk)
]


print("\n" + "=" * 65)
print(" THREE-LAYER RISK ANALYSIS")
print("=" * 65)


print(
    f"\nValid cells: {len(valid_risk)}"
)


print(
    f"Minimum risk: "
    f"{np.min(valid_risk):.2f}"
)


print(
    f"Maximum risk: "
    f"{np.max(valid_risk):.2f}"
)


print(
    f"Average risk: "
    f"{np.mean(valid_risk):.2f}"
)


# ------------------------------------------------------------
# RISK CLASSES
# ------------------------------------------------------------

safe = np.sum(
    valid_risk < 30
)

caution = np.sum(
    (valid_risk >= 30)
    &
    (valid_risk < 60)
)

dangerous = np.sum(
    (valid_risk >= 60)
    &
    (valid_risk < 80)
)

critical = np.sum(
    valid_risk >= 80
)


print("\nRISK DISTRIBUTION")

print(
    f"SAFE:       {safe}"
)

print(
    f"CAUTION:    {caution}"
)

print(
    f"DANGEROUS:  {dangerous}"
)

print(
    f"CRITICAL:   {critical}"
)


# ------------------------------------------------------------
# SAVE SUMMARY
# ------------------------------------------------------------

print("\n✓ Total environmental risk map saved:")

print(
    OUTPUT_FILE
)


print("\n" + "=" * 65)
print(" THREE-LAYER RISK MODEL COMPLETE 🚀")
print("=" * 65)