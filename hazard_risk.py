import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from pyproj import Transformer


print("=" * 60)
print(" LUNAR CODEX - SIZE-AWARE ICEBERG HAZARD ENGINE")
print("=" * 60)


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

ICE_FILE = DATA_DIR / "sh_20230526.nc"
ICEBERG_FILE = DATA_DIR / "antarctic_icebergs.csv"

OUTPUT_FILE = DATA_DIR / "hazard_risk_20230526.npy"


# ------------------------------------------------------------
# CHECK FILES
# ------------------------------------------------------------

print("\nChecking files...")

if not ICE_FILE.exists():
    raise FileNotFoundError(f"Missing ice file:\n{ICE_FILE}")

if not ICEBERG_FILE.exists():
    raise FileNotFoundError(
        f"Missing iceberg CSV:\n{ICEBERG_FILE}"
    )

print("✓ USNIC ice grid found")
print("✓ Antarctic iceberg CSV found")


# ------------------------------------------------------------
# LOAD USNIC GRID
# ------------------------------------------------------------

print("\nLoading Antarctic grid...")

ice_ds = xr.open_dataset(ICE_FILE)

ice_data = ice_ds["tc_mid"].values[0]

x = ice_ds["x"].values
y = ice_ds["y"].values

ROWS, COLS = ice_data.shape

print(f"Ice grid: {ice_data.shape}")
print("CRS: EPSG:6932")


# ------------------------------------------------------------
# LOAD ICEBERG CSV
# ------------------------------------------------------------

print("\nLoading iceberg data...")

df = pd.read_csv(ICEBERG_FILE)

print(f"Total iceberg records: {len(df)}")

print("\nColumns detected:")

for column in df.columns:
    print(" -", column)


# ------------------------------------------------------------
# NORMALIZE COLUMN NAMES
# ------------------------------------------------------------

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("(", "", regex=False)
    .str.replace(")", "", regex=False)
)

print("\nNormalized columns:")
print(df.columns.tolist())


# ------------------------------------------------------------
# FIND REQUIRED COLUMNS
# ------------------------------------------------------------

def find_column(columns, possible_names):

    for name in possible_names:

        if name in columns:
            return name

    return None


lat_column = find_column(
    df.columns,
    ["latitude", "lat", "lat_dd"]
)

lon_column = find_column(
    df.columns,
    ["longitude", "lon", "long", "lon_dd"]
)

length_column = find_column(
    df.columns,
    ["length_nm", "length"]
)

width_column = find_column(
    df.columns,
    ["width_nm", "width"]
)


if lat_column is None:
    raise ValueError(
        "Latitude column not found."
    )

if lon_column is None:
    raise ValueError(
        "Longitude column not found."
    )

if length_column is None:
    raise ValueError(
        "Length column not found."
    )

if width_column is None:
    raise ValueError(
        "Width column not found."
    )


print(f"\nLatitude column: {lat_column}")
print(f"Longitude column: {lon_column}")
print(f"Length column: {length_column}")
print(f"Width column: {width_column}")


# ------------------------------------------------------------
# CLEAN DATA
# ------------------------------------------------------------

df[lat_column] = pd.to_numeric(
    df[lat_column],
    errors="coerce"
)

df[lon_column] = pd.to_numeric(
    df[lon_column],
    errors="coerce"
)

df[length_column] = pd.to_numeric(
    df[length_column],
    errors="coerce"
)

df[width_column] = pd.to_numeric(
    df[width_column],
    errors="coerce"
)


df = df.dropna(
    subset=[
        lat_column,
        lon_column,
        length_column,
        width_column
    ]
)


# Antarctic region

df = df[
    df[lat_column] <= -50
]


print(
    f"\nValid Antarctic iceberg records: {len(df)}"
)


# ------------------------------------------------------------
# COORDINATE TRANSFORMATION
# ------------------------------------------------------------

print("\nConverting iceberg coordinates...")


transformer = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:6932",
    always_xy=True
)


# ------------------------------------------------------------
# CREATE HAZARD GRID
# ------------------------------------------------------------

hazard_risk = np.zeros(
    (ROWS, COLS),
    dtype=np.float32
)


# ------------------------------------------------------------
# GRID RESOLUTION
# ------------------------------------------------------------

# Estimate grid resolution in metres.

x_resolution = float(
    np.median(np.abs(np.diff(x)))
)

y_resolution = float(
    np.median(np.abs(np.diff(y)))
)

grid_resolution = (
    x_resolution + y_resolution
) / 2


print(
    f"\nApproximate grid resolution: "
    f"{grid_resolution / 1000:.2f} km"
)


# ------------------------------------------------------------
# PROCESS EACH ICEBERG
# ------------------------------------------------------------

print("\nBuilding size-aware hazard field...")


for index, iceberg in df.iterrows():

    latitude = iceberg[lat_column]
    longitude = iceberg[lon_column]

    length_nm = iceberg[length_column]
    width_nm = iceberg[width_column]


    # --------------------------------------------------------
    # Convert geographic position
    # --------------------------------------------------------

    px, py = transformer.transform(
        longitude,
        latitude
    )


    # --------------------------------------------------------
    # Check grid bounds
    # --------------------------------------------------------

    if (
        px < np.min(x)
        or px > np.max(x)
        or py < np.min(y)
        or py > np.max(y)
    ):
        continue


    # --------------------------------------------------------
    # Find nearest grid cell
    # --------------------------------------------------------

    column = int(
        np.abs(x - px).argmin()
    )

    row = int(
        np.abs(y - py).argmin()
    )


    # --------------------------------------------------------
    # Convert iceberg dimensions
    # --------------------------------------------------------

    # 1 nautical mile = 1852 metres

    length_m = length_nm * 1852
    width_m = width_nm * 1852


    # Use the larger dimension to determine
    # the primary hazard radius.

    largest_dimension = max(
        length_m,
        width_m
    )


    # --------------------------------------------------------
    # Size-aware safety radius
    # --------------------------------------------------------

    # Base safety distance around iceberg
    base_radius_m = 5000


    # Additional radius based on iceberg size
    size_radius_m = (
        largest_dimension * 1.5
    )


    hazard_radius_m = (
        base_radius_m
        +
        size_radius_m
    )


    # Convert physical radius to grid cells

    radius_cells = max(
        3,
        int(
            hazard_radius_m
            /
            grid_resolution
        )
    )


    # Prevent extremely large computation areas

    radius_cells = min(
        radius_cells,
        60
    )


    # --------------------------------------------------------
    # Hazard field
    # --------------------------------------------------------

    r_min = max(
        0,
        row - radius_cells
    )

    r_max = min(
        ROWS,
        row + radius_cells + 1
    )

    c_min = max(
        0,
        column - radius_cells
    )

    c_max = min(
        COLS,
        column + radius_cells + 1
    )


    for r in range(
        r_min,
        r_max
    ):

        for c in range(
            c_min,
            c_max
        ):

            distance_cells = np.sqrt(
                (r - row) ** 2
                +
                (c - column) ** 2
            )


            distance_m = (
                distance_cells
                *
                grid_resolution
            )


            # ------------------------------------------------
            # Hazard calculation
            # ------------------------------------------------

            if distance_m <= 1000:

                risk = 100

            elif distance_m <= 0.25 * hazard_radius_m:

                risk = 90

            elif distance_m <= 0.50 * hazard_radius_m:

                risk = 70

            elif distance_m <= 0.75 * hazard_radius_m:

                risk = 50

            elif distance_m <= hazard_radius_m:

                risk = 30

            else:

                risk = 0


            hazard_risk[r, c] = max(
                hazard_risk[r, c],
                risk
            )


    print(
        f"Iceberg {index + 1:02d}: "
        f"{length_nm:.1f} × {width_nm:.1f} NM | "
        f"radius ≈ {hazard_radius_m / 1000:.1f} km"
    )


# ------------------------------------------------------------
# MASK LAND
# ------------------------------------------------------------

hazard_risk[
    ice_data == 119
] = np.nan


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

np.save(
    OUTPUT_FILE,
    hazard_risk
)


# ------------------------------------------------------------
# STATISTICS
# ------------------------------------------------------------

print("\n" + "=" * 60)
print(" SIZE-AWARE ICEBERG HAZARD ANALYSIS")
print("=" * 60)


print(
    f"\nHazard grid: {hazard_risk.shape}"
)

print(
    f"Minimum hazard: "
    f"{np.nanmin(hazard_risk):.2f}"
)

print(
    f"Maximum hazard: "
    f"{np.nanmax(hazard_risk):.2f}"
)

print(
    f"Average hazard: "
    f"{np.nanmean(hazard_risk):.2f}"
)


print("\nHAZARD DISTRIBUTION")


print(
    "LOW:       ",
    np.sum(
        (hazard_risk >= 0)
        &
        (hazard_risk < 30)
    )
)


print(
    "CAUTION:   ",
    np.sum(
        (hazard_risk >= 30)
        &
        (hazard_risk < 60)
    )
)


print(
    "DANGEROUS: ",
    np.sum(
        (hazard_risk >= 60)
        &
        (hazard_risk < 80)
    )
)


print(
    "CRITICAL:  ",
    np.sum(
        hazard_risk >= 80
    )
)


print("\n✓ Size-aware hazard map saved:")
print(OUTPUT_FILE)


print("\n" + "=" * 60)
print(" SIZE-AWARE HAZARD ENGINE COMPLETE 🚀")
print("=" * 60)