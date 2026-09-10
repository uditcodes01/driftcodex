# --------------------------------------
# LUNAR CODEX - COMBINED ENVIRONMENTAL
# RISK MAP
# --------------------------------------

import matplotlib.pyplot as plt
import numpy as np

from combined_risk import (
    combined_risk,
    get_risk_level
)


plt.figure(figsize=(12, 10))


plt.imshow(
    combined_risk,
    cmap="RdYlGn_r",
    interpolation="nearest",
    vmin=0,
    vmax=100
)


colorbar = plt.colorbar()

colorbar.set_label(
    "Combined Environmental Risk (0-100)"
)


plt.title(
    "LUNAR CODEX\n"
    "AI-Powered Antarctic Environmental Risk Map\n"
    "USNIC Ice + ERA5 Weather",
    fontsize=16
)


plt.xlabel(
    "Navigation Grid X"
)

plt.ylabel(
    "Navigation Grid Y"
)


# --------------------------------------
# RISK LEGEND
# --------------------------------------

plt.text(
    0.5,
    -0.08,
    "Risk Model: "
    "60% Ice Risk + 40% Weather Risk",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11
)


# --------------------------------------
# STATISTICS
# --------------------------------------

valid = combined_risk[
    ~np.isnan(combined_risk)
]


average_risk = np.mean(valid)

maximum_risk = np.max(valid)


print()
print("======================================")
print(" LUNAR CODEX - COMBINED RISK MAP")
print("======================================")
print()

print(
    "Average combined risk:",
    round(
        float(average_risk),
        2
    )
)

print(
    "Maximum combined risk:",
    round(
        float(maximum_risk),
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
        & (valid < 60)
    )
)

print(
    "DANGEROUS:",
    np.sum(
        (valid >= 60)
        & (valid < 80)
    )
)

print(
    "CRITICAL:",
    np.sum(
        valid >= 80
    )
)

print()

print("--------------------------------------")
print(" COMBINED RISK MAP READY 🚀")
print("--------------------------------------")

print()
print("Close the map window to finish.")


plt.tight_layout()

plt.show()