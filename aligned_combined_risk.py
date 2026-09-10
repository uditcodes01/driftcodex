# --------------------------------------
# LUNAR CODEX - ALIGNED ENVIRONMENTAL
# RISK MODEL
# USNIC ICE + GEOSPATIAL ERA5 WEATHER
# --------------------------------------

import numpy as np

from ice_risk import ice_risk


# --------------------------------------
# LOAD ALIGNED WEATHER DATA
# --------------------------------------

WEATHER_FILE = "../data/aligned_wind_20230526.npy"

aligned_wind = np.load(
    WEATHER_FILE
)


# --------------------------------------
# CHECK GRID ALIGNMENT
# --------------------------------------

if ice_risk.shape != aligned_wind.shape:

    raise ValueError(
        "ERROR: Ice and weather grids "
        "do not have the same shape."
    )


# --------------------------------------
# CALCULATE WEATHER RISK
# --------------------------------------

def calculate_weather_risk(wind_speed):

    weather_risk = np.full(
        wind_speed.shape,
        np.nan,
        dtype=np.float32
    )

    valid = ~np.isnan(wind_speed)

    # 0-5 m/s → SAFE
    mask = (
        valid
        & (wind_speed < 5)
    )

    weather_risk[mask] = (
        wind_speed[mask]
        / 5
        * 20
    )

    # 5-10 m/s → CAUTION
    mask = (
        valid
        & (wind_speed >= 5)
        & (wind_speed < 10)
    )

    weather_risk[mask] = (
        20
        +
        (wind_speed[mask] - 5)
        / 5
        * 20
    )

    # 10-15 m/s → DANGEROUS
    mask = (
        valid
        & (wind_speed >= 10)
        & (wind_speed < 15)
    )

    weather_risk[mask] = (
        40
        +
        (wind_speed[mask] - 10)
        / 5
        * 30
    )

    # 15+ m/s → CRITICAL
    mask = (
        valid
        & (wind_speed >= 15)
    )

    weather_risk[mask] = 100

    return weather_risk


weather_risk = calculate_weather_risk(
    aligned_wind
)


# --------------------------------------
# COMBINE ICE + WEATHER
# --------------------------------------

combined_risk = np.full(
    ice_risk.shape,
    np.nan,
    dtype=np.float32
)


valid_cells = (
    ~np.isnan(ice_risk)
    &
    ~np.isnan(weather_risk)
)


# --------------------------------------
# RISK WEIGHTS
# --------------------------------------

ICE_WEIGHT = 0.60
WEATHER_WEIGHT = 0.40


combined_risk[valid_cells] = (

    ice_risk[valid_cells]
    * ICE_WEIGHT

    +

    weather_risk[valid_cells]
    * WEATHER_WEIGHT
)


# --------------------------------------
# RISK CLASSIFICATION
# --------------------------------------

def get_risk_level(risk):

    if risk < 30:
        return "SAFE"

    elif risk < 60:
        return "CAUTION"

    elif risk < 80:
        return "DANGEROUS"

    else:
        return "CRITICAL"


# --------------------------------------
# ANALYSIS
# --------------------------------------

if __name__ == "__main__":

    valid = combined_risk[
        ~np.isnan(combined_risk)
    ]

    print()
    print("======================================")
    print(" LUNAR CODEX - ALIGNED RISK MODEL")
    print("======================================")
    print()

    print("DATA SOURCES:")
    print()
    print("USNIC Antarctic Sea Ice")
    print("ERA5 Antarctic Weather")

    print()
    print("======================================")
    print(" GRID ALIGNMENT")
    print("======================================")
    print()

    print(
        "Ice grid:",
        ice_risk.shape
    )

    print(
        "Weather grid:",
        aligned_wind.shape
    )

    print(
        "Combined grid:",
        combined_risk.shape
    )

    print()
    print("✓ Ice and weather grids match.")

    print()
    print("======================================")
    print(" RISK MODEL")
    print("======================================")
    print()

    print(
        "Ice weight:",
        ICE_WEIGHT * 100,
        "%"
    )

    print(
        "Weather weight:",
        WEATHER_WEIGHT * 100,
        "%"
    )

    print()

    print(
        "Formula:"
    )

    print(
        "Combined Risk = "
        "0.60 × Ice Risk + "
        "0.40 × Weather Risk"
    )

    print()
    print("======================================")
    print(" WEATHER ANALYSIS")
    print("======================================")
    print()

    print(
        "Minimum wind:",
        round(
            float(np.nanmin(aligned_wind)),
            2
        ),
        "m/s"
    )

    print(
        "Maximum wind:",
        round(
            float(np.nanmax(aligned_wind)),
            2
        ),
        "m/s"
    )

    print(
        "Average wind:",
        round(
            float(np.nanmean(aligned_wind)),
            2
        ),
        "m/s"
    )

    print()
    print("======================================")
    print(" COMBINED RISK ANALYSIS")
    print("======================================")
    print()

    print(
        "Valid cells:",
        len(valid)
    )

    print(
        "Minimum risk:",
        round(
            float(np.nanmin(valid)),
            2
        )
    )

    print(
        "Maximum risk:",
        round(
            float(np.nanmax(valid)),
            2
        )
    )

    print(
        "Average risk:",
        round(
            float(np.nanmean(valid)),
            2
        )
    )

    print()

    print(
        "SAFE:",
        np.sum(valid < 30)
    )

    print(
        "CAUTION:",
        np.sum(
            (valid >= 30)
            &
            (valid < 60)
        )
    )

    print(
        "DANGEROUS:",
        np.sum(
            (valid >= 60)
            &
            (valid < 80)
        )
    )

    print(
        "CRITICAL:",
        np.sum(valid >= 80)
    )

    print()
    print("--------------------------------------")
    print(" ALIGNED ENVIRONMENTAL RISK READY 🚀")
    print("--------------------------------------")