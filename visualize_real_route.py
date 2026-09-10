# --------------------------------------
# LUNAR CODEX - REAL ANTARCTIC
# ROUTE VISUALIZATION
# --------------------------------------

import matplotlib.pyplot as plt
import numpy as np

from real_route_optimizer import (
    navigation_grid,
    choose_start_and_goal,
    find_route
)


# ======================================
# CHOOSE START + DESTINATION
# ======================================

start, goal = choose_start_and_goal()

if start is None or goal is None:
    print("ERROR: Could not find valid start and destination.")
    exit()


# ======================================
# CALCULATE ROUTE
# ======================================

route, total_cost = find_route(
    start,
    goal
)

if route is None:
    print("ERROR: No feasible route found.")
    exit()


# ======================================
# ROUTE COORDINATES
# ======================================

route_rows = [
    point[0]
    for point in route
]

route_cols = [
    point[1]
    for point in route
]


# ======================================
# CREATE MAP
# ======================================

plt.figure(
    figsize=(12, 9)
)

plt.imshow(
    navigation_grid,
    cmap="RdYlGn_r",
    interpolation="nearest",
    vmin=0,
    vmax=100
)


# ======================================
# DRAW AI ROUTE
# ======================================

plt.plot(
    route_cols,
    route_rows,
    linewidth=3,
    marker="o",
    markersize=3,
    label="AI Optimized Route"
)


# ======================================
# START
# ======================================

plt.scatter(
    start[1],
    start[0],
    s=300,
    marker="*",
    label="START"
)


# ======================================
# DESTINATION
# ======================================

plt.scatter(
    goal[1],
    goal[0],
    s=300,
    marker="X",
    label="DESTINATION"
)


# ======================================
# LABELS
# ======================================

plt.xlabel(
    "Navigation Grid X"
)

plt.ylabel(
    "Navigation Grid Y"
)

plt.title(
    "LUNAR CODEX\n"
    "AI-Powered Antarctic Route Optimization\n"
    "Real USNIC Sea-Ice Data",
    fontsize=16
)


# ======================================
# COLORBAR
# ======================================

colorbar = plt.colorbar()

colorbar.set_label(
    "Ice Risk / Ice Concentration (%)"
)


# ======================================
# ROUTE ANALYSIS
# ======================================

route_risks = [
    navigation_grid[row, col]
    for row, col in route
]

average_risk = np.mean(route_risks)

maximum_risk = np.max(route_risks)


# ======================================
# DISPLAY INFORMATION
# ======================================

plt.text(
    0.5,
    -0.08,
    f"Route Cells: {len(route)}   |   "
    f"Average Ice Risk: {average_risk:.1f}   |   "
    f"Maximum Ice Risk: {maximum_risk:.1f}   |   "
    f"Route Cost: {total_cost:.1f}",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=11
)


plt.legend()

plt.tight_layout()


# ======================================
# TERMINAL OUTPUT
# ======================================

print()

print("======================================")
print("   LUNAR CODEX - REAL ROUTE MAP")
print("======================================")

print()

print("START:", start)

print(
    "Start ice risk:",
    round(navigation_grid[start], 2)
)

print()

print("DESTINATION:", goal)

print(
    "Destination ice risk:",
    round(navigation_grid[goal], 2)
)

print()

print("Route cells:", len(route))

print(
    "Average ice risk:",
    round(average_risk, 2)
)

print(
    "Maximum ice risk:",
    round(maximum_risk, 2)
)

print(
    "Total route cost:",
    round(total_cost, 2)
)

print()

print(
    "Real Antarctic route visualization ready!"
)

print(
    "Close the map window to finish."
)


plt.show()