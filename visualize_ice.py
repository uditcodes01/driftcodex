# --------------------------------------
# LUNAR CODEX - REAL ANTARCTIC ICE MAP
# --------------------------------------

import matplotlib.pyplot as plt
import numpy as np

from ice_risk import ice_risk


# --------------------------------------
# CREATE FIGURE
# --------------------------------------

plt.figure(figsize=(10, 10))


# --------------------------------------
# DISPLAY ICE RISK
# --------------------------------------

plt.imshow(
    ice_risk,
    cmap="RdYlGn_r",
    interpolation="nearest",
    vmin=0,
    vmax=100
)


# --------------------------------------
# COLORBAR
# --------------------------------------

colorbar = plt.colorbar()

colorbar.set_label(
    "Ice Risk / Ice Concentration (%)"
)


# --------------------------------------
# TITLE
# --------------------------------------

plt.title(
    "LUNAR CODEX\n"
    "Real Antarctic Ice Risk Map\n"
    "USNIC Data - 26 May 2023",
    fontsize=16
)


# --------------------------------------
# AXIS LABELS
# --------------------------------------

plt.xlabel("Grid X")

plt.ylabel("Grid Y")


# --------------------------------------
# STATISTICS
# --------------------------------------

valid_cells = ice_risk[
    ~np.isnan(ice_risk)
]

average_risk = np.mean(
    valid_cells
)


print()
print("======================================")
print("   REAL ANTARCTIC ICE MAP")
print("======================================")
print()

print(
    "Valid cells:",
    len(valid_cells)
)

print(
    "Average ice risk:",
    round(average_risk, 2)
)

print()

print(
    "Map generated successfully!"
)

print(
    "Close the map window to finish."
)


# --------------------------------------
# DISPLAY MAP
# --------------------------------------

plt.tight_layout()

plt.show()