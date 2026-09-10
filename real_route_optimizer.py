# --------------------------------------
# LUNAR CODEX - REAL ANTARCTIC
# RISK-AWARE ROUTE OPTIMIZER
# --------------------------------------

import heapq
import numpy as np

from ice_risk import ice_risk


# ======================================
# DOWNSAMPLE REAL DATA
# ======================================

SCALE = 10

navigation_grid = ice_risk[::SCALE, ::SCALE]

ROWS = navigation_grid.shape[0]
COLS = navigation_grid.shape[1]


# ======================================
# RISK LEVEL
# ======================================

def get_risk_level(risk):

    if risk < 30:
        return "SAFE"

    elif risk < 60:
        return "CAUTION"

    elif risk < 80:
        return "DANGEROUS"

    else:
        return "CRITICAL"


# ======================================
# FIND VALID CELLS
# ======================================

def find_valid_cells():

    cells = []

    for row in range(ROWS):

        for col in range(COLS):

            risk = navigation_grid[row, col]

            if not np.isnan(risk):

                cells.append((row, col))

    return cells


# ======================================
# CHOOSE SAFE START + DISTANT DESTINATION
# ======================================

def choose_start_and_goal():

    valid_cells = find_valid_cells()

    if len(valid_cells) < 2:

        return None, None


    # ----------------------------------
    # SAFE START CANDIDATES
    # ----------------------------------

    safe_starts = [
        cell
        for cell in valid_cells
        if 5 <= navigation_grid[cell] <= 30
    ]


    # If not enough safe cells,
    # allow moderate-risk cells.

    if len(safe_starts) < 2:

        safe_starts = [
            cell
            for cell in valid_cells
            if navigation_grid[cell] <= 40
        ]


    if len(safe_starts) < 2:

        return None, None


    # ----------------------------------
    # SORT STARTS
    # ----------------------------------

    safe_starts.sort(
        key=lambda cell: (
            cell[0] + cell[1],
            navigation_grid[cell]
        )
    )


    # Choose a safe start from the region
    # instead of automatically choosing
    # the highest-risk area.

    start = safe_starts[len(safe_starts) // 3]


    # ----------------------------------
    # DESTINATION CANDIDATES
    # ----------------------------------

    destinations = [
        cell
        for cell in valid_cells
        if 10 <= navigation_grid[cell] <= 70
    ]


    if len(destinations) < 2:

        destinations = valid_cells


    # ----------------------------------
    # FIND DISTANT DESTINATION
    # ----------------------------------

    best_goal = None
    best_score = -1


    for candidate in destinations:

        distance = (
            abs(candidate[0] - start[0])
            + abs(candidate[1] - start[1])
        )

        risk = navigation_grid[candidate]

        # Prefer destinations that are far away
        # while avoiding extremely risky destinations.

        score = distance - (risk * 0.1)


        if score > best_score:

            best_score = score
            best_goal = candidate


    goal = best_goal


    return start, goal


# ======================================
# MOVEMENT COST
# ======================================

def get_cost(position):

    row, col = position

    risk = navigation_grid[row, col]


    if np.isnan(risk):

        return float("inf")


    distance_cost = 1

    risk_cost = risk * 0.5


    # Strongly penalize dangerous ice.

    if risk >= 60:

        risk_cost = risk * 3


    return distance_cost + risk_cost


# ======================================
# HEURISTIC
# ======================================

def heuristic(position, goal):

    return (
        abs(position[0] - goal[0])
        + abs(position[1] - goal[1])
    )


# ======================================
# NEIGHBOURS
# ======================================

def get_neighbors(position):

    row, col = position

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    neighbors = []


    for dr, dc in directions:

        new_row = row + dr
        new_col = col + dc


        if (
            0 <= new_row < ROWS
            and 0 <= new_col < COLS
        ):

            if not np.isnan(
                navigation_grid[new_row, new_col]
            ):

                neighbors.append(
                    (new_row, new_col)
                )


    return neighbors


# ======================================
# A* ROUTE OPTIMIZATION
# ======================================

def find_route(start, goal):

    priority_queue = []

    heapq.heappush(
        priority_queue,
        (0, start)
    )


    came_from = {}

    cost_so_far = {
        start: 0
    }


    while priority_queue:

        _, current = heapq.heappop(
            priority_queue
        )


        if current == goal:

            break


        for neighbor in get_neighbors(current):

            new_cost = (
                cost_so_far[current]
                + get_cost(neighbor)
            )


            if (
                neighbor not in cost_so_far
                or new_cost < cost_so_far[neighbor]
            ):

                cost_so_far[neighbor] = new_cost


                priority = (
                    new_cost
                    + heuristic(
                        neighbor,
                        goal
                    )
                )


                heapq.heappush(
                    priority_queue,
                    (priority, neighbor)
                )


                came_from[neighbor] = current


    # ----------------------------------
    # CHECK IF ROUTE EXISTS
    # ----------------------------------

    if goal not in cost_so_far:

        return None, None


    # ----------------------------------
    # RECONSTRUCT ROUTE
    # ----------------------------------

    route = []

    current = goal


    while current != start:

        route.append(current)

        current = came_from[current]


    route.append(start)

    route.reverse()


    return route, cost_so_far[goal]


# ======================================
# ANALYZE ROUTE
# ======================================

def analyze_route(route):

    risks = []

    safe = 0
    caution = 0
    dangerous = 0
    critical = 0


    for row, col in route:

        risk = navigation_grid[row, col]

        risks.append(risk)

        level = get_risk_level(risk)


        if level == "SAFE":

            safe += 1

        elif level == "CAUTION":

            caution += 1

        elif level == "DANGEROUS":

            dangerous += 1

        else:

            critical += 1


    return (
        safe,
        caution,
        dangerous,
        critical,
        np.mean(risks),
        np.max(risks)
    )


# ======================================
# MAIN
# ======================================

def main():

    print()

    print("======================================")
    print(" LUNAR CODEX - REAL DATA NAVIGATION")
    print("======================================")

    print()


    print(
        "Original data:",
        ice_risk.shape[0],
        "x",
        ice_risk.shape[1]
    )


    print(
        "Navigation grid:",
        ROWS,
        "x",
        COLS
    )


    print(
        "Downsampling factor:",
        SCALE
    )


    print()


    print("Risk levels:")

    print("0-30   = SAFE")
    print("30-60  = CAUTION")
    print("60-80  = DANGEROUS")
    print("80-100 = CRITICAL")


    print()


    # ----------------------------------
    # SELECT START + DESTINATION
    # ----------------------------------

    start, goal = choose_start_and_goal()


    if start is None:

        print(
            "ERROR: Could not find valid cells."
        )

        return


    print("======================================")
    print("     AI ENVIRONMENTAL ANALYSIS")
    print("======================================")


    print()


    print(
        "Valid navigation cells:",
        len(find_valid_cells())
    )


    print()


    print(
        "START:",
        start
    )


    print(
        "Start ice risk:",
        round(
            navigation_grid[start],
            2
        )
    )


    print(
        "Start level:",
        get_risk_level(
            navigation_grid[start]
        )
    )


    print()


    print(
        "DESTINATION:",
        goal
    )


    print(
        "Destination ice risk:",
        round(
            navigation_grid[goal],
            2
        )
    )


    print(
        "Destination level:",
        get_risk_level(
            navigation_grid[goal]
        )
    )


    print()


    print("======================================")
    print("        CALCULATING AI ROUTE")
    print("======================================")


    print()


    # ----------------------------------
    # CALCULATE ROUTE
    # ----------------------------------

    route, total_cost = find_route(
        start,
        goal
    )


    if route is None:

        print(
            "No feasible route found."
        )

        return


    # ----------------------------------
    # ANALYZE ROUTE
    # ----------------------------------

    (
        safe,
        caution,
        dangerous,
        critical,
        average_risk,
        maximum_risk
    ) = analyze_route(route)


    print("======================================")
    print("          AI OPTIMIZED ROUTE")
    print("======================================")


    print()


    print(
        "Number of navigation cells:",
        len(route)
    )


    print()


    # ----------------------------------
    # FIRST PART
    # ----------------------------------

    print("First part of route:")


    for point in route[:10]:

        risk = navigation_grid[point]


        print(
            f"{point} "
            f"Risk: {risk:.1f} "
            f"-> {get_risk_level(risk)}"
        )


    # ----------------------------------
    # MIDDLE
    # ----------------------------------

    if len(route) > 20:

        print()

        print(
            "......................"
        )

        print()


    # ----------------------------------
    # FINAL PART
    # ----------------------------------

    print("Final part of route:")


    for point in route[-10:]:

        risk = navigation_grid[point]


        print(
            f"{point} "
            f"Risk: {risk:.1f} "
            f"-> {get_risk_level(risk)}"
        )


    # ----------------------------------
    # ROUTE ANALYSIS
    # ----------------------------------

    print()

    print("======================================")
    print("       ROUTE DECISION ANALYSIS")
    print("======================================")


    print()


    print(
        "Total navigation cells:",
        len(route)
    )


    print(
        "SAFE cells:",
        safe
    )


    print(
        "CAUTION cells:",
        caution
    )


    print(
        "DANGEROUS cells:",
        dangerous
    )


    print(
        "CRITICAL cells:",
        critical
    )


    print()


    print(
        "Average route ice risk:",
        round(
            average_risk,
            2
        )
    )


    print(
        "Maximum route ice risk:",
        round(
            maximum_risk,
            2
        )
    )


    print(
        "Maximum risk level:",
        get_risk_level(
            maximum_risk
        )
    )


    print()


    print(
        "Total route cost:",
        round(
            total_cost,
            2
        )
    )


    # ----------------------------------
    # AI DECISION
    # ----------------------------------

    print()

    print("======================================")
    print("             AI DECISION")
    print("======================================")


    print()


    if dangerous == 0:

        print(
            "✓ AI avoided dangerous ice."
        )

    else:

        print(
            "✓ AI minimized dangerous ice exposure."
        )


    if critical == 0:

        print(
            "✓ AI avoided critical areas."
        )

    else:

        print(
            "⚠ Critical-risk cells were encountered."
        )


    if average_risk < 30:

        print(
            "✓ Route maintained low average ice risk."
        )

    elif average_risk < 60:

        print(
            "→ Route maintained moderate ice risk."
        )

    else:

        print(
            "⚠ Route contains substantial ice risk."
        )


    print()


    print(
        "FINAL STRATEGY:"
    )


    print(
        "Minimize environmental risk while"
    )


    print(
        "maintaining a feasible Antarctic route."
    )


    print()


    print("--------------------------------------")
    print(" REAL ANTARCTIC AI ROUTE READY 🚀")
    print("--------------------------------------")


# ======================================
# RUN PROGRAM
# ======================================

if __name__ == "__main__":

    main()