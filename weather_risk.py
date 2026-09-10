# --------------------------------------
# LUNAR CODEX - REAL ANTARCTIC
# WEATHER RISK MODEL
# --------------------------------------

import xarray as xr
import numpy as np


# ======================================
# LOAD ERA5 WEATHER DATA
# ======================================

FILE_PATH = "../data/31de44eda6ce7cd9ec3799efb3a80d75.nc"

ds = xr.open_dataset(FILE_PATH)


# ======================================
# EXTRACT WEATHER VARIABLES
# ======================================

u10 = ds["u10"].values[0]

v10 = ds["v10"].values[0]

temperature = ds["t2m"].values[0]


# ======================================
# CALCULATE WIND SPEED
# ======================================

wind_speed = np.sqrt(
    u10 ** 2 + v10 ** 2
)


# ======================================
# CALCULATE WEATHER RISK
# ======================================

def calculate_weather_risk(wind_speed):

    weather_risk = np.zeros_like(
        wind_speed,
        dtype=np.float32
    )

    # 0-5 m/s → SAFE
    weather_risk[wind_speed < 5] = (
        wind_speed[wind_speed < 5] / 5 * 20
    )

    # 5-10 m/s → CAUTION
    mask = (
        (wind_speed >= 5)
        & (wind_speed < 10)
    )

    weather_risk[mask] = (
        20
        + (wind_speed[mask] - 5) / 5 * 20
    )

    # 10-15 m/s → DANGEROUS
    mask = (
        (wind_speed >= 10)
        & (wind_speed < 15)
    )

    weather_risk[mask] = (
        40
        + (wind_speed[mask] - 10) / 5 * 30
    )

    # 15+ m/s → CRITICAL
    mask = wind_speed >= 15

    weather_risk[mask] = 100

    return weather_risk


weather_risk = calculate_weather_risk(
    wind_speed
)


# ======================================
# MAIN
# ======================================

if __name__ == "__main__":

    print()
    print("======================================")
    print(" LUNAR CODEX - REAL WEATHER RISK")
    print("======================================")
    print()

    print("Dataset:")
    print("ERA5 Antarctic Weather Data")

    print()

    print("Date:")
    print("2023-05-26")

    print()

    print("Weather grid:")
    print(
        weather_risk.shape[0],
        "x",
        weather_risk.shape[1]
    )

    print()

    print("Wind speed:")
    print(
        "Minimum:",
        round(float(np.nanmin(wind_speed)), 2),
        "m/s"
    )

    print(
        "Maximum:",
        round(float(np.nanmax(wind_speed)), 2),
        "m/s"
    )

    print(
        "Average:",
        round(float(np.nanmean(wind_speed)), 2),
        "m/s"
    )

    print()

    print("Temperature:")

    print(
        "Minimum:",
        round(float(np.nanmin(temperature)), 2),
        "K"
    )

    print(
        "Maximum:",
        round(float(np.nanmax(temperature)), 2),
        "K"
    )

    print(
        "Average:",
        round(float(np.nanmean(temperature)), 2),
        "K"
    )

    print()

    print("Weather risk:")

    print(
        "Minimum:",
        round(float(np.nanmin(weather_risk)), 2)
    )

    print(
        "Maximum:",
        round(float(np.nanmax(weather_risk)), 2)
    )

    print(
        "Average:",
        round(float(np.nanmean(weather_risk)), 2)
    )

    print()

    print("--------------------------------------")
    print(" REAL ANTARCTIC WEATHER RISK READY 🚀")
    print("--------------------------------------")