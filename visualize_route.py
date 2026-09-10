import matplotlib.pyplot as plt

from risk_grid import risk_grid
from route_optimizer import find_route, get_risk_level


# --------------------------------------
# HEADER
# --------------------------------------

print("======================================")
print("   LUNAR CODEX - ROUTE VISUALIZER")
print("======================================")
print()


# --------------------------------------
# GET START
# --------------------------------------

start_row = int(
    input("Enter START row (0-3): ")
)

start_col = int(
    input("Enter START column (0-4): ")
)

start = (start_row, start_col)


# --------------------------------------
# GET DESTINATION
# --------------------------------------

goal_row = int(
    input("Enter DESTINATION row (0-3): ")
)

goal_col = int(
    input("Enter DESTINATION column (0-4): ")
)

goal = (goal_row, goal_col)


# --------------------------------------
# FIND AI ROUTE
# --------------------------------------

route, total_cost = find_route(
    start,
    goal
)


# --------------------------------------
# CREATE MAP
# --------------------------------------

plt.figure(figsize=(12, 7))

plt.imshow(
    risk_grid,
    cmap="RdYlGn_r",
    interpolation="nearest",
    vmin=0,
    vmax=100
)


# --------------------------------------
# DISPLAY RISK + LEVEL
# --------------------------------------

for row in range(len(risk_grid)):

    for col in range(len(risk_grid[0])):

        risk = risk_grid[row][col]

        level = get_risk_level(risk)

        plt.text(
            col,
            row,
            f"{risk:.1f}\n{level}",
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold"
        )


# --------------------------------------
# GET ROUTE COORDINATES
# --------------------------------------

route_rows = [
    position[0]
    for position in route
]

route_cols = [
    position[1]
    for position in route
]


# --------------------------------------
# DRAW AI ROUTE
# --------------------------------------

plt.plot(
    route_cols,
    route_rows,
    marker="o",
    linewidth=4,
    markersize=9,
    label="AI Optimized Route"
)


# --------------------------------------
# START MARKER
# --------------------------------------

plt.scatter(
    start[1],
    start[0],
    s=300,
    marker="*",
    label="START"
)


# --------------------------------------
# DESTINATION MARKER
# --------------------------------------

plt.scatter(
    goal[1],
    goal[0],
    s=300,
    marker="X",
    label="DESTINATION"
)


# --------------------------------------
# AXIS LABELS
# --------------------------------------

plt.xlabel("Grid Column")

plt.ylabel("Grid Row")

plt.xticks(
    range(len(risk_grid[0]))
)

plt.yticks(
    range(len(risk_grid))
)


# --------------------------------------
# COLORBAR
# --------------------------------------

colorbar = plt.colorbar()

colorbar.set_label(
    "Environmental Risk (0–100)"
)


# --------------------------------------
# TITLE
# --------------------------------------

plt.title(
    "LUNAR CODEX\n"
    "AI-Powered Antarctic Risk-Aware Navigation",
    fontsize=16
)


# --------------------------------------
# ROUTE STATISTICS
# --------------------------------------

risks = [
    risk_grid[row][col]
    for row, col in route
]

maximum_risk = max(risks)

maximum_level = get_risk_level(
    maximum_risk
)


plt.text(
    0.5,
    -0.15,
    f"Route Cost: {total_cost:.2f}   |   "
    f"Maximum Risk: {maximum_risk:.1f} "
    f"({maximum_level})",
    transform=plt.gca().transAxes,
    ha="center",
    fontsize=12
)


# --------------------------------------
# LEGEND
# --------------------------------------

plt.legend()


# --------------------------------------
# DISPLAY
# --------------------------------------

plt.tight_layout()

plt.show()