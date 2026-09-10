import numpy as np
import xarray as xr
import heapq
from pathlib import Path


# ============================================================
# LUNAR CODEX - RISK-BUFFERED A* ROUTE OPTIMIZER
# ============================================================

print("=" * 60)
print(" LUNAR CODEX - RISK-BUFFERED A* ROUTE OPTIMIZER")
print("=" * 60)


# ============================================================
# FILE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

ICE_FILE = DATA_DIR / "sh_20230526.nc"
WIND_FILE = DATA_DIR / "aligned_wind_20230526.npy"


# ============================================================
# START AND DESTINATION
# ============================================================

START = (402, 490)
DESTINATION = (501, 51)


# ============================================================
# CHECK FILES
# ============================================================

print("\nChecking data files...")

if not ICE_FILE.exists():
    raise FileNotFoundError(
        f"Ice data file not found:\n{ICE_FILE}"
    )

if not WIND_FILE.exists():
    raise FileNotFoundError(
        f"Weather data file not found:\n{WIND_FILE}"
    )

print("✓ Ice data found")
print("✓ Weather data found")


# ============================================================
# LOAD ICE DATA
# ============================================================

print("\nLoading ice data...")

ice_ds = xr.open_dataset(ICE_FILE)

ice_data = ice_ds["tc_mid"].values[0]

print(f"Ice grid: {ice_data.shape}")


# ============================================================
# CONVERT ICE DATA TO ICE RISK
# ============================================================

ice_risk = np.full(
    ice_data.shape,
    np.nan,
    dtype=np.float32
)

# Normal ice concentration: 0-100
real_ice = (
    (ice_data >= 0)
    &
    (ice_data <= 100)
)

ice_risk[real_ice] = ice_data[real_ice]

# Fast ice
ice_risk[ice_data == 110] = 100

# Usually ocean
ice_risk[ice_data == 118] = 0

# Land
ice_risk[ice_data == 119] = np.nan


# ============================================================
# LOAD WEATHER DATA
# ============================================================

print("\nLoading weather data...")

wind_speed = np.load(WIND_FILE)

print(f"Weather grid: {wind_speed.shape}")


# ============================================================
# CHECK GRID
# ============================================================

if ice_risk.shape != wind_speed.shape:
    raise ValueError(
        f"Grid mismatch!\n"
        f"Ice grid: {ice_risk.shape}\n"
        f"Weather grid: {wind_speed.shape}"
    )

print("\n✓ Ice and weather grids match")


# ============================================================
# WEATHER RISK
# ============================================================

print("\nCalculating weather risk...")

weather_risk = np.full(
    wind_speed.shape,
    np.nan,
    dtype=np.float32
)


# ------------------------------------------------------------
# Wind < 5 m/s
# Risk: 0-20
# ------------------------------------------------------------

mask = wind_speed < 5

weather_risk[mask] = (
    wind_speed[mask] / 5
) * 20


# ------------------------------------------------------------
# Wind 5-10 m/s
# Risk: 20-40
# ------------------------------------------------------------

mask = (
    (wind_speed >= 5)
    &
    (wind_speed < 10)
)

weather_risk[mask] = (
    20
    +
    ((wind_speed[mask] - 5) / 5) * 20
)


# ------------------------------------------------------------
# Wind 10-15 m/s
# Risk: 40-70
# ------------------------------------------------------------

mask = (
    (wind_speed >= 10)
    &
    (wind_speed < 15)
)

weather_risk[mask] = (
    40
    +
    ((wind_speed[mask] - 10) / 5) * 30
)


# ------------------------------------------------------------
# Wind >= 15 m/s
# Risk: 100
# ------------------------------------------------------------

mask = wind_speed >= 15

weather_risk[mask] = 100


# ============================================================
# COMBINED ENVIRONMENTAL RISK
# ============================================================

print("\nCalculating combined environmental risk...")

combined_risk = (
    0.60 * ice_risk
    +
    0.40 * weather_risk
)

# Keep land unavailable
combined_risk[np.isnan(ice_risk)] = np.nan


# ============================================================
# GRID INFORMATION
# ============================================================

rows, cols = combined_risk.shape

print(f"Combined grid: {combined_risk.shape}")


# ============================================================
# LOCAL / BUFFERED RISK
# ============================================================

print("\nPreparing risk buffer...")


def get_buffered_risk(r, c):
    """
    Calculates environmental risk around a cell.

    Uses a 3x3 neighborhood.

    This makes the AI aware of nearby dangerous
    areas instead of looking only at one cell.
    """

    # 3x3 neighborhood boundaries
    r1 = max(0, r - 1)
    r2 = min(rows, r + 2)

    c1 = max(0, c - 1)
    c2 = min(cols, c + 2)

    neighborhood = combined_risk[
        r1:r2,
        c1:c2
    ]

    # Remove land / invalid cells
    valid_values = neighborhood[
        ~np.isnan(neighborhood)
    ]

    if len(valid_values) == 0:
        return np.inf

    current_risk = combined_risk[r, c]

    if np.isnan(current_risk):
        return np.inf

    local_average = np.mean(valid_values)

    local_maximum = np.max(valid_values)

    # Buffered risk formula
    buffered_risk = (
        0.60 * current_risk
        +
        0.25 * local_average
        +
        0.15 * local_maximum
    )

    return buffered_risk


# ============================================================
# MOVEMENT COST
# ============================================================

def movement_cost(r, c):
    """
    Converts environmental risk into movement cost.

    Higher risk = higher cost.

    Critical areas are forbidden.
    """

    risk = combined_risk[r, c]

    # Land / invalid cell
    if np.isnan(risk):
        return np.inf

    buffered_risk = get_buffered_risk(r, c)

    # --------------------------------------------------------
    # Critical
    # --------------------------------------------------------

    if risk >= 80:
        return np.inf

    if buffered_risk >= 80:
        return np.inf

    # --------------------------------------------------------
    # Very dangerous
    # --------------------------------------------------------

    if buffered_risk >= 70:
        return 1 + buffered_risk * 12

    # --------------------------------------------------------
    # Dangerous
    # --------------------------------------------------------

    if buffered_risk >= 60:
        return 1 + buffered_risk * 8

    # --------------------------------------------------------
    # Caution
    # --------------------------------------------------------

    if buffered_risk >= 30:
        return 1 + buffered_risk * 2

    # --------------------------------------------------------
    # Safe
    # --------------------------------------------------------

    return 1 + buffered_risk * 0.3


# ============================================================
# A* HEURISTIC
# ============================================================

def heuristic(a, b):
    """
    Manhattan distance between two grid cells.
    """

    return (
        abs(a[0] - b[0])
        +
        abs(a[1] - b[1])
    )


# ============================================================
# A* SEARCH
# ============================================================

print("\nCalculating risk-buffered route...")


open_set = []

heapq.heappush(
    open_set,
    (
        heuristic(
            START,
            DESTINATION
        ),
        START
    )
)


came_from = {}

g_score = {
    START: 0
}

visited = set()

route_found = False


# ============================================================
# SEARCH LOOP
# ============================================================

while open_set:

    _, current = heapq.heappop(open_set)

    # Skip already processed cells
    if current in visited:
        continue

    visited.add(current)

    # --------------------------------------------------------
    # Destination reached
    # --------------------------------------------------------

    if current == DESTINATION:

        route_found = True

        break

    r, c = current

    # --------------------------------------------------------
    # Four possible movements
    # --------------------------------------------------------

    neighbors = [
        (r - 1, c),     # Up
        (r + 1, c),     # Down
        (r, c - 1),     # Left
        (r, c + 1)      # Right
    ]

    # --------------------------------------------------------
    # Check neighbors
    # --------------------------------------------------------

    for nr, nc in neighbors:

        # Outside grid
        if nr < 0 or nr >= rows:
            continue

        if nc < 0 or nc >= cols:
            continue

        neighbor = (nr, nc)

        # Calculate movement cost
        cost = movement_cost(
            nr,
            nc
        )

        # Cannot enter
        if np.isinf(cost):
            continue

        # New route cost
        tentative_g = (
            g_score[current]
            +
            cost
        )

        # Better route found
        if (
            neighbor not in g_score
            or tentative_g < g_score[neighbor]
        ):

            came_from[neighbor] = current

            g_score[neighbor] = tentative_g

            f_score = (
                tentative_g
                +
                heuristic(
                    neighbor,
                    DESTINATION
                )
            )

            heapq.heappush(
                open_set,
                (
                    f_score,
                    neighbor
                )
            )


# ============================================================
# ROUTE CHECK
# ============================================================

if not route_found:

    print("\n" + "=" * 60)
    print(" ❌ NO ROUTE FOUND")
    print("=" * 60)

    raise SystemExit


# ============================================================
# RECONSTRUCT ROUTE
# ============================================================

print("\nReconstructing route...")


route = []

current = DESTINATION


while current != START:

    route.append(current)

    current = came_from[current]


route.append(START)

route.reverse()


# ============================================================
# ROUTE RISK VALUES
# ============================================================

route_risks = np.array([
    combined_risk[r, c]
    for r, c in route
])


route_buffered_risks = np.array([
    get_buffered_risk(r, c)
    for r, c in route
])


# ============================================================
# ROUTE STATISTICS
# ============================================================

average_risk = np.mean(
    route_risks
)

maximum_risk = np.max(
    route_risks
)

average_buffered_risk = np.mean(
    route_buffered_risks
)

maximum_buffered_risk = np.max(
    route_buffered_risks
)

total_cost = g_score[
    DESTINATION
]


# ============================================================
# RISK COUNTS
# ============================================================

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


# ============================================================
# DISTANCE
# ============================================================

distance = np.sqrt(
    (DESTINATION[0] - START[0]) ** 2
    +
    (DESTINATION[1] - START[1]) ** 2
)


# ============================================================
# PRINT FINAL RESULTS
# ============================================================

print("\n" + "=" * 60)
print(" RISK-BUFFERED ROUTE FOUND 🚀")
print("=" * 60)


# ------------------------------------------------------------
# Start
# ------------------------------------------------------------

print("\nSTART")

print(
    f"Row: {START[0]}"
)

print(
    f"Column: {START[1]}"
)

print(
    f"Risk: {combined_risk[START]:.2f}"
)


# ------------------------------------------------------------
# Destination
# ------------------------------------------------------------

print("\nDESTINATION")

print(
    f"Row: {DESTINATION[0]}"
)

print(
    f"Column: {DESTINATION[1]}"
)

print(
    f"Risk: {combined_risk[DESTINATION]:.2f}"
)


# ------------------------------------------------------------
# Distance
# ------------------------------------------------------------

print(
    f"\nDistance: {distance:.2f} grid units"
)


# ------------------------------------------------------------
# Route statistics
# ------------------------------------------------------------

print("\nROUTE STATISTICS")
print("-" * 45)

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
    f"Average buffered risk: "
    f"{average_buffered_risk:.2f}"
)

print(
    f"Maximum buffered risk: "
    f"{maximum_buffered_risk:.2f}"
)

print(
    f"Total route cost: "
    f"{total_cost:.2f}"
)


# ------------------------------------------------------------
# Risk distribution
# ------------------------------------------------------------

print("\nRISK DISTRIBUTION")

print(
    f"SAFE:      {safe_count}"
)

print(
    f"CAUTION:   {caution_count}"
)

print(
    f"DANGEROUS: {dangerous_count}"
)

print(
    f"CRITICAL:  {critical_count}"
)


# ============================================================
# FIRST 10 ROUTE CELLS
# ============================================================

print("\nFIRST 10 ROUTE CELLS")
print("-" * 60)


for cell in route[:10]:

    r, c = cell

    risk = combined_risk[r, c]

    buffered = get_buffered_risk(
        r,
        c
    )

    # Risk level
    if risk < 30:

        level = "SAFE"

    elif risk < 60:

        level = "CAUTION"

    elif risk < 80:

        level = "DANGEROUS"

    else:

        level = "CRITICAL"

    print(
        f"{cell} | "
        f"Risk: {risk:.2f} | "
        f"Buffered: {buffered:.2f} | "
        f"{level}"
    )


# ============================================================
# SAVE OPTIMIZED ROUTE
# ============================================================

route_file = (
    DATA_DIR
    /
    "optimized_route.npy"
)

np.save(
    route_file,
    np.array(route)
)


print("\n✓ Optimized route saved:")

print(
    route_file
)


# ============================================================
# GENERATE BUFFERED RISK MAP
# ============================================================

print("\nGenerating buffered risk map...")

buffered_risk_map = np.full(
    combined_risk.shape,
    np.nan,
    dtype=np.float32
)


# ------------------------------------------------------------
# Calculate buffered risk for every valid cell
# ------------------------------------------------------------

for r in range(rows):

    for c in range(cols):

        if not np.isnan(
            combined_risk[r, c]
        ):

            buffered_risk_map[r, c] = (
                get_buffered_risk(
                    r,
                    c
                )
            )


# ============================================================
# SAVE BUFFERED RISK MAP
# ============================================================

buffered_file = (
    DATA_DIR
    /
    "buffered_risk_20230526.npy"
)

np.save(
    buffered_file,
    buffered_risk_map
)


print(
    "✓ Buffered risk map saved:"
)

print(
    buffered_file
)


# ============================================================
# FINISHED
# ============================================================

print("\n" + "=" * 60)
print(" RISK-BUFFERED A* COMPLETE 🚀")
print("=" * 60)