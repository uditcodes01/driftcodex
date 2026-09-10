# --------------------------------------
# LUNAR CODEX - REAL ANTARCTIC
# WEATHER RISK MAP
# --------------------------------------

import matplotlib.pyplot as plt

from weather_risk import (
    weather_risk,
    wind_speed
)


plt.figure(figsize=(14, 8))


plt.imshow(
    weather_risk,
    cmap="RdYlGn_r",
    interpolation="nearest",
    vmin=0,
    vmax=100
)


colorbar = plt.colorbar()

colorbar.set_label(
    "Weather Risk (0-100)"
)


plt.title(
    "LUNAR CODEX\n"
    "Real Antarctic Weather Risk Map\n"
    "ERA5 Data - 26 May 2023",
    fontsize=16
)


plt.xlabel("Longitude Grid")
plt.ylabel("Latitude Grid")


plt.text(
    0.5,
    -0.08,
    f"Average Weather Risk: "
    f"{weather_risk.mean():.1f}/100   |   "
    f"Average Wind Speed: "
    f"{wind_speed.mean():.1f} m/s",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11
)


plt.tight_layout()


print()
print("======================================")
print(" LUNAR CODEX - WEATHER RISK MAP")
print("======================================")

print(
    "Average weather risk:",
    round(float(weather_risk.mean()), 2)
)

print(
    "Average wind speed:",
    round(float(wind_speed.mean()), 2),
    "m/s"
)

print()
print("Weather risk map generated!")
print("Close the map window to finish.")


plt.show()