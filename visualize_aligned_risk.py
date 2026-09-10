import numpy as np
import matplotlib.pyplot as plt

from ice_risk import ice_risk

WEATHER_FILE = "../data/aligned_wind_20230526.npy"

aligned_wind = np.load(WEATHER_FILE)


def calculate_weather_risk(wind_speed):
    weather_risk = np.full(wind_speed.shape, np.nan, dtype=np.float32)

    valid = ~np.isnan(wind_speed)

    mask = valid & (wind_speed < 5)
    weather_risk[mask] = wind_speed[mask] / 5 * 20

    mask = valid & (wind_speed >= 5) & (wind_speed < 10)
    weather_risk[mask] = 20 + (wind_speed[mask] - 5) / 5 * 20

    mask = valid & (wind_speed >= 10) & (wind_speed < 15)
    weather_risk[mask] = 40 + (wind_speed[mask] - 10) / 5 * 30

    mask = valid & (wind_speed >= 15)
    weather_risk[mask] = 100

    return weather_risk


weather_risk = calculate_weather_risk(aligned_wind)

combined_risk = np.full(ice_risk.shape, np.nan, dtype=np.float32)

valid_cells = ~np.isnan(ice_risk) & ~np.isnan(weather_risk)

combined_risk[valid_cells] = (
    ice_risk[valid_cells] * 0.60
    + weather_risk[valid_cells] * 0.40
)


plt.figure(figsize=(10, 8))

image = plt.imshow(
    combined_risk,
    origin="upper",
    cmap="RdYlGn_r",
    vmin=0,
    vmax=100
)

plt.colorbar(image, label="Environmental Risk (0-100)")

plt.title(
    "LUNAR CODEX - Antarctic Environmental Risk Map\n"
    "USNIC Ice + ERA5 Weather"
)

plt.xlabel("USNIC Grid X")
plt.ylabel("USNIC Grid Y")

plt.tight_layout()

plt.show()