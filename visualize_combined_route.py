# --------------------------------------
# LUNAR CODEX - COMBINED RISK + AI ROUTE
# REAL ANTARCTIC ENVIRONMENTAL MAP
# --------------------------------------

import matplotlib.pyplot as plt
import numpy as np

from combined_risk import combined_risk
from combined_route_optimizer import (
    choose_start_and_goal,
    find_route
)


# --------------------------------------
# FIND START AND DESTINATION
# --------------------------------------

start, goal = choose_start_and_goal()


if start is None or goal is None:

    print("ERROR: Could not find valid start and destination.")

    exit()


# --------------------------------------
# CALCULATE AI ROUTE
# --------------------------------------

route, total_cost = find_route(
    start,
    goal
)


if route is None:

    print("ERROR: No feasible route found.")

    exit()


# --------------------------------------
# EXTRACT ROUTE COORDINATES
# --------------------------------------

route_rows = [
    point[0]
    for point in route
]

route_cols = [
    point[1]
    for point in route
]


# --------------------------------------
# CREATE MAP
# --------------------------------------

plt.figure(
    figsize=(14, 10)
)


plt.imshow(
    combined_risk,
    cmap="RdYlGn_r",
    interpolation="nearest",
    vmin=0,
    vmax=100
)


# --------------------------------------
# DRAW AI ROUTE
# --------------------------------------

plt.plot(
    route_cols,
    route_rows,
    linewidth=3,
    marker="o",
    markersize=2,
    label="AI Optimized Route"
)


# --------------------------------------
# START MARKER
# --------------------------------------

plt.scatter(
    start[1],
    start[0],
    s=400,
    marker="*",
    label="START"
)


# --------------------------------------
# DESTINATION MARKER
# --------------------------------------

plt.scatter(
    goal[1],
    goal[0],
    s=400,
    marker="X",
    label="DESTINATION"
)


# --------------------------------------
# LABELS
# --------------------------------------

plt.xlabel(
    "Navigation Grid X"
)

plt.ylabel(
    "Navigation Grid Y"
)


plt.title(
    "LUNAR CODEX\n"
    "AI-Powered Antarctic Risk-Aware Navigation\n"
    "USNIC Ice + ERA5 Weather",
    fontsize=17
)


# --------------------------------------
# COLORBAR
# --------------------------------------

colorbar = plt.colorbar()

colorbar.set_label(
    "Combined Environmental Risk (0-100)"
)


# --------------------------------------
# ROUTE STATISTICS
# --------------------------------------

route_risks = [

    combined_risk[row, col]

    for row, col in route

]


average_risk = np.mean(
    route_risks
)


maximum_risk = np.max(
    route_risks
)


safe_cells = np.sum(
    np.array(route_risks) < 30
)


caution_cells = np.sum(
    (
        np.array(route_risks) >= 30
    )
    &
    (
        np.array(route_risks) < 60
    )
)


dangerous_cells = np.sum(
    (
        np.array(route_risks) >= 60
    )
    &
    (
        np.array(route_risks) < 80
    )
)


critical_cells = np.sum(
    np.array(route_risks) >= 80
)


# --------------------------------------
# DISPLAY STATISTICS
# --------------------------------------

statistics_text = (

    f"Route Cells: {len(route)}   |   "

    f"Average Risk: {average_risk:.2f}   |   "

    f"Maximum Risk: {maximum_risk:.2f}\n"

    f"SAFE: {safe_cells}   |   "

    f"CAUTION: {caution_cells}   |   "

    f"DANGEROUS: {dangerous_cells}   |   "

    f"CRITICAL: {critical_cells}   |   "

    f"Route Cost: {total_cost:.2f}"

)


plt.text(
    0.5,
    -0.08,
    statistics_text,
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11
)


# --------------------------------------
# LEGEND
# --------------------------------------

plt.legend(
    loc="upper right"
)


# --------------------------------------
# FINAL OUTPUT
# --------------------------------------

plt.tight_layout()


print()
print("======================================")
print(" LUNAR CODEX - FINAL AI ROUTE MAP")
print("======================================")
print()

print(
    "START:",
    start
)

print(
    "Start risk:",
    round(
        float(combined_risk[start]),
        2
    )
)

print()

print(
    "DESTINATION:",
    goal
)

print(
    "Destination risk:",
    round(
        float(combined_risk[goal]),
        2
    )
)

print()

print(
    "Route cells:",
    len(route)
)

print(
    "Average environmental risk:",
    round(
        float(average_risk),
        2
    )
)

print(
    "Maximum environmental risk:",
    round(
        float(maximum_risk),
        2
    )
)

print(
    "SAFE cells:",
    safe_cells
)

print(
    "CAUTION cells:",
    caution_cells
)

print(
    "DANGEROUS cells:",
    dangerous_cells
)

print(
    "CRITICAL cells:",
    critical_cells
)

print()

print(
    "Total route cost:",
    round(
        float(total_cost),
        2
    )
)

print()

print("--------------------------------------")
print(" FINAL AI ROUTE VISUALIZATION READY 🚀")
print("--------------------------------------")

print()
print("Close the map window to finish.")


# --------------------------------------
# SHOW MAP
# --------------------------------------

plt.show()