import numpy as np
from pathlib import Path
import heapq


print("=" * 65)
print(" LUNAR CODEX - THREE-LAYER A* ROUTE OPTIMIZER")
print("=" * 65)


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

RISK_FILE = DATA_DIR / "total_risk_20230526.npy"
ROUTE_FILE = DATA_DIR / "three_layer_route_20230526.npy"


# ------------------------------------------------------------
# LOAD RISK MAP
# ------------------------------------------------------------

print("\nChecking risk data...")

if not RISK_FILE.exists():
    raise FileNotFoundError(f"Missing file:\n{RISK_FILE}")

print("✓ Three-layer risk map found")

risk_grid = np.load(RISK_FILE)

print(f"Risk grid: {risk_grid.shape}")


# ------------------------------------------------------------
# START / DESTINATION
# ------------------------------------------------------------

START = (402, 490)
DESTINATION = (501, 51)

print("\nSTART")
print(f"Row: {START[0]}")
print(f"Column: {START[1]}")
print(f"Risk: {risk_grid[START]:.2f}")

print("\nDESTINATION")
print(f"Row: {DESTINATION[0]}")
print(f"Column: {DESTINATION[1]}")
print(f"Risk: {risk_grid[DESTINATION]:.2f}")


# ------------------------------------------------------------
# RISK LEVEL
# ------------------------------------------------------------

def risk_level(risk):

    if risk < 30:
        return "SAFE"

    if risk < 60:
        return "CAUTION"

    if risk < 80:
        return "DANGEROUS"

    return "CRITICAL"


# ------------------------------------------------------------
# MOVEMENT COST
# ------------------------------------------------------------

def movement_cost(risk):

    if np.isnan(risk):
        return np.inf

    # Critical areas are completely forbidden
    if risk >= 80:
        return np.inf

    # Strongly avoid dangerous areas
    if risk >= 60:
        return 1 + risk * 8

    # Moderate penalty for caution
    if risk >= 30:
        return 1 + risk * 2

    # Prefer safe areas
    return 1 + risk * 0.3


# ------------------------------------------------------------
# HEURISTIC
# ------------------------------------------------------------

def heuristic(a, b):

    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ------------------------------------------------------------
# NEIGHBORS
# ------------------------------------------------------------

def get_neighbors(node):

    r, c = node

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    for dr, dc in directions:

        nr = r + dr
        nc = c + dc

        if (
            0 <= nr < risk_grid.shape[0]
            and
            0 <= nc < risk_grid.shape[1]
        ):
            yield (nr, nc)


# ------------------------------------------------------------
# A* SEARCH
# ------------------------------------------------------------

print("\nCalculating safest route...")

open_set = []

heapq.heappush(
    open_set,
    (heuristic(START, DESTINATION), START)
)

came_from = {}

g_score = {
    START: 0
}

visited = set()

route_found = False


while open_set:

    _, current = heapq.heappop(open_set)

    if current in visited:
        continue

    visited.add(current)

    if current == DESTINATION:

        route_found = True
        break

    for neighbor in get_neighbors(current):

        risk = risk_grid[neighbor]

        cost = movement_cost(risk)

        if np.isinf(cost):
            continue

        new_cost = (
            g_score[current]
            +
            cost
        )

        if (
            neighbor not in g_score
            or
            new_cost < g_score[neighbor]
        ):

            g_score[neighbor] = new_cost

            came_from[neighbor] = current

            f_score = (
                new_cost
                +
                heuristic(
                    neighbor,
                    DESTINATION
                )
            )

            heapq.heappush(
                open_set,
                (f_score, neighbor)
            )


# ------------------------------------------------------------
# CHECK ROUTE
# ------------------------------------------------------------

if not route_found:

    print("\n❌ NO SAFE ROUTE FOUND")

    raise SystemExit


# ------------------------------------------------------------
# RECONSTRUCT ROUTE
# ------------------------------------------------------------

print("\nReconstructing route...")

route = []

current = DESTINATION

while current != START:

    route.append(current)

    current = came_from[current]

route.append(START)

route.reverse()

route = np.array(
    route,
    dtype=np.int32
)


# ------------------------------------------------------------
# SAVE ROUTE
# ------------------------------------------------------------

np.save(
    ROUTE_FILE,
    route
)


# ------------------------------------------------------------
# ROUTE STATISTICS
# ------------------------------------------------------------

route_risks = np.array([
    risk_grid[
        r,
        c
    ]
    for r, c in route
])


average_risk = np.mean(route_risks)

maximum_risk = np.max(route_risks)

safe_count = np.sum(
    route_risks < 30
)

caution_count = np.sum(
    (route_risks >= 30)
    &
    (route_risks < 60)
)

dangerous_count = np.sum(
    (route_risks >= 60)
    &
    (route_risks < 80)
)

critical_count = np.sum(
    route_risks >= 80
)


distance = heuristic(
    START,
    DESTINATION
)

total_cost = g_score[DESTINATION]


# ------------------------------------------------------------
# RESULTS
# ------------------------------------------------------------

print("\n" + "=" * 65)
print(" THREE-LAYER ROUTE FOUND 🚀")
print("=" * 65)

print("\nSTART")
print(
    f"Row: {START[0]}"
)
print(
    f"Column: {START[1]}"
)
print(
    f"Risk: {risk_grid[START]:.2f}"
)


print("\nDESTINATION")
print(
    f"Row: {DESTINATION[0]}"
)
print(
    f"Column: {DESTINATION[1]}"
)
print(
    f"Risk: {risk_grid[DESTINATION]:.2f}"
)


print("\nROUTE STATISTICS")

print(
    f"Route cells: {len(route)}"
)

print(
    f"Average risk: {average_risk:.2f}"
)

print(
    f"Maximum risk: {maximum_risk:.2f}"
)

print(
    f"Distance: {distance:.2f} grid units"
)

print(
    f"Total route cost: {total_cost:.2f}"
)


print("\nRISK DISTRIBUTION")

print(
    f"SAFE:       {safe_count}"
)

print(
    f"CAUTION:    {caution_count}"
)

print(
    f"DANGEROUS:  {dangerous_count}"
)

print(
    f"CRITICAL:   {critical_count}"
)


print("\nFIRST 10 ROUTE CELLS")

for r, c in route[:10]:

    risk = risk_grid[r, c]

    print(
        f"({r}, {c}) | "
        f"Risk: {risk:.2f} | "
        f"{risk_level(risk)}"
    )


print("\n✓ Route saved:")

print(
    ROUTE_FILE
)


print("\n" + "=" * 65)
print(" THREE-LAYER A* COMPLETE 🚀")
print("=" * 65)