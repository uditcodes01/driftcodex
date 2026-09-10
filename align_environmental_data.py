# --------------------------------------
# LUNAR CODEX - GEOSPATIAL ALIGNMENT
# USNIC ICE + ERA5 WEATHER
# --------------------------------------

import xarray as xr
import numpy as np

from rasterio.warp import reproject
from rasterio.enums import Resampling
from rasterio.transform import from_bounds


# --------------------------------------
# FILE PATHS
# --------------------------------------

ICE_FILE = "../data/sh_20230526.nc"
WEATHER_FILE = "../data/31de44eda6ce7cd9ec3799efb3a80d75.nc"


# --------------------------------------
# LOAD DATA
# --------------------------------------

print()
print("======================================")
print(" LUNAR CODEX - GEOSPATIAL ALIGNMENT")
print("======================================")
print()

print("Loading USNIC ice data...")

ice_ds = xr.open_dataset(ICE_FILE)

ice = ice_ds["tc_mid"].values[0]


print("Loading ERA5 weather data...")

weather_ds = xr.open_dataset(WEATHER_FILE)

u10 = weather_ds["u10"].values[0]
v10 = weather_ds["v10"].values[0]


# --------------------------------------
# CALCULATE WIND SPEED
# --------------------------------------

wind_speed = np.sqrt(
    u10 ** 2 +
    v10 ** 2
)


# --------------------------------------
# GET ERA5 COORDINATES
# --------------------------------------

latitudes = weather_ds["latitude"].values
longitudes = weather_ds["longitude"].values


print()
print("ERA5 grid:")
print("Rows:", len(latitudes))
print("Columns:", len(longitudes))


# --------------------------------------
# GET USNIC GRID
# --------------------------------------

x = ice_ds["x"].values
y = ice_ds["y"].values


print()
print("USNIC grid:")
print("Rows:", len(y))
print("Columns:", len(x))


# --------------------------------------
# CRS INFORMATION
# --------------------------------------

print()
print("USNIC CRS:")
print("EPSG:6932")
print("WGS 84 / NSIDC EASE-Grid 2.0 South")


# --------------------------------------
# ERA5 SOURCE TRANSFORM
# --------------------------------------

# ERA5 uses geographic coordinates:
#
# Longitude: -180 to +180
# Latitude:  -50 to -90
#
# CRS: EPSG:4326

source_transform = from_bounds(
    float(longitudes.min()),
    float(latitudes.min()),
    float(longitudes.max()),
    float(latitudes.max()),
    len(longitudes),
    len(latitudes)
)


# --------------------------------------
# USNIC DESTINATION TRANSFORM
# --------------------------------------

destination_transform = from_bounds(
    float(x.min()),
    float(y.min()),
    float(x.max()),
    float(y.max()),
    len(x),
    len(y)
)


# --------------------------------------
# CREATE OUTPUT ARRAY
# --------------------------------------

aligned_wind = np.full(
    ice.shape,
    np.nan,
    dtype=np.float32
)


# --------------------------------------
# REPROJECT ERA5
# TO USNIC GRID
# --------------------------------------

print()
print("======================================")
print(" REPROJECTING ERA5 WEATHER")
print("======================================")
print()

print("Source CRS: EPSG:4326")
print("Destination CRS: EPSG:6932")
print()

print("Resampling weather data...")


reproject(
    source=wind_speed.astype(np.float32),
    destination=aligned_wind,

    src_transform=source_transform,
    src_crs="EPSG:4326",

    dst_transform=destination_transform,
    dst_crs="EPSG:6932",

    resampling=Resampling.bilinear
)


# --------------------------------------
# MASK LAND
# --------------------------------------

aligned_wind[
    ice == 119
] = np.nan


# --------------------------------------
# SAVE ALIGNED DATA
# --------------------------------------

output_file = "../data/aligned_wind_20230526.npy"

np.save(
    output_file,
    aligned_wind
)


# --------------------------------------
# ANALYSIS
# --------------------------------------

valid = aligned_wind[
    ~np.isnan(aligned_wind)
]


print()
print("======================================")
print(" ALIGNMENT COMPLETE")
print("======================================")
print()

print(
    "Original ERA5 grid:",
    wind_speed.shape
)

print(
    "USNIC target grid:",
    ice.shape
)

print(
    "Aligned weather grid:",
    aligned_wind.shape
)

print()

print(
    "Valid aligned cells:",
    len(valid)
)

print(
    "Minimum wind speed:",
    round(
        float(np.nanmin(aligned_wind)),
        2
    ),
    "m/s"
)

print(
    "Maximum wind speed:",
    round(
        float(np.nanmax(aligned_wind)),
        2
    ),
    "m/s"
)

print(
    "Average wind speed:",
    round(
        float(np.nanmean(aligned_wind)),
        2
    ),
    "m/s"
)

print()

print("Saved aligned data:")
print(output_file)

print()

print("--------------------------------------")
print(" GEOSPATIAL ALIGNMENT READY 🚀")
print("--------------------------------------")