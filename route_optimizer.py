from risk_grid import risk_grid
import heapq


# --------------------------------------
# GRID DIMENSIONS
# --------------------------------------

ROWS = len(risk_grid)
COLS = len(risk_grid[0])


# --------------------------------------
# RISK CLASSIFICATION
# --------------------------------------

def get_risk_level(risk):

    if risk < 30:
        return "SAFE"

    elif risk < 60:
        return "CAUTION"

    elif risk < 80:
        return "DANGEROUS"

    else:
        return "CRITICAL"


# --------------------------------------
# MOVEMENT COST
# --------------------------------------

def get_cost(position, goal):

    row, col = position
    risk = risk_grid[row][col]

    distance_cost = 1

    risk_cost = risk * 0.5

    # Strong penalty for dangerous areas
    if risk >= 60:
        risk_cost = risk * 3

    return distance_cost + risk_cost


# --------------------------------------
# HEURISTIC
# --------------------------------------

def heuristic(position, goal):

    row, col = position

    return abs(row - goal[0]) + abs(col - goal[1])


# --------------------------------------
# FIND NEIGHBOURS
# --------------------------------------

def get_neighbors(position):

    row, col = position

    neighbors = []

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    for dr, dc in directions:

        new_row = row + dr
        new_col = col + dc

        if 0 <= new_row < ROWS and 0 <= new_col < COLS:

            neighbors.append((new_row, new_col))

    return neighbors


# --------------------------------------
# A* ROUTE FINDING
# --------------------------------------

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

        current_priority, current = heapq.heappop(
            priority_queue
        )

        if current == goal:
            break

        for neighbor in get_neighbors(current):

            row, col = neighbor

            neighbor_risk = risk_grid[row][col]

            # Critical zones are forbidden
            # unless they are the destination.
            if neighbor_risk >= 80 and neighbor != goal:
                continue

            new_cost = (
                cost_so_far[current]
                + get_cost(neighbor, goal)
            )

            if (
                neighbor not in cost_so_far
                or new_cost < cost_so_far[neighbor]
            ):

                cost_so_far[neighbor] = new_cost

                priority = (
                    new_cost
                    + heuristic(neighbor, goal)
                )

                heapq.heappush(
                    priority_queue,
                    (priority, neighbor)
                )

                came_from[neighbor] = current

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


# --------------------------------------
# ROUTE ANALYSIS
# --------------------------------------

def analyze_route(route):

    risks = []

    safe_count = 0
    caution_count = 0
    dangerous_count = 0
    critical_count = 0

    for row, col in route:

        risk = risk_grid[row][col]

        risks.append(risk)

        level = get_risk_level(risk)

        if level == "SAFE":
            safe_count += 1

        elif level == "CAUTION":
            caution_count += 1

        elif level == "DANGEROUS":
            dangerous_count += 1

        elif level == "CRITICAL":
            critical_count += 1

    maximum_risk = max(risks)

    average_risk = sum(risks) / len(risks)

    return (
        safe_count,
        caution_count,
        dangerous_count,
        critical_count,
        maximum_risk,
        average_risk
    )


# --------------------------------------
# MAIN PROGRAM
# --------------------------------------

def main():

    print()
    print("======================================")
    print("   LUNAR CODEX - ROUTE OPTIMIZER")
    print("======================================")
    print()

    print(
        "Grid size:",
        ROWS,
        "rows x",
        COLS,
        "columns"
    )

    print()

    print("Risk Classification:")
    print("0-30   = SAFE")
    print("30-60  = CAUTION")
    print("60-80  = DANGEROUS")
    print("80-100 = CRITICAL")

    print()

    # ----------------------------------
    # START
    # ----------------------------------

    start_row = int(
        input("Enter START row (0-3): ")
    )

    start_col = int(
        input("Enter START column (0-4): ")
    )

    start = (start_row, start_col)

    # ----------------------------------
    # DESTINATION
    # ----------------------------------

    goal_row = int(
        input("Enter DESTINATION row (0-3): ")
    )

    goal_col = int(
        input("Enter DESTINATION column (0-4): ")
    )

    goal = (goal_row, goal_col)

    # ----------------------------------
    # FIND ROUTE
    # ----------------------------------

    route, total_cost = find_route(
        start,
        goal
    )

    # ----------------------------------
    # DISPLAY ROUTE
    # ----------------------------------

    print()
    print("======================================")
    print("        AI OPTIMIZED ROUTE")
    print("======================================")

    for position in route:

        row, col = position

        risk = risk_grid[row][col]

        level = get_risk_level(risk)

        print(
            f"{position} "
            f"Risk: {risk:.1f} "
            f"→ {level}"
        )

    # ----------------------------------
    # ANALYZE ROUTE
    # ----------------------------------

    (
        safe_count,
        caution_count,
        dangerous_count,
        critical_count,
        maximum_risk,
        average_risk
    ) = analyze_route(route)

    # ----------------------------------
    # ROUTE DECISION ANALYSIS
    # ----------------------------------

    print()
    print("======================================")
    print("       ROUTE DECISION ANALYSIS")
    print("======================================")

    print()
    print(f"Total cells: {len(route)}")

    print(f"SAFE cells: {safe_count}")
    print(f"CAUTION cells: {caution_count}")
    print(f"DANGEROUS cells: {dangerous_count}")
    print(f"CRITICAL cells: {critical_count}")

    print()
    print(
        f"Average Route Risk: "
        f"{average_risk:.2f}/100"
    )

    print(
        f"Maximum Route Risk: "
        f"{maximum_risk:.1f}/100"
    )

    print(
        f"Maximum Risk Level: "
        f"{get_risk_level(maximum_risk)}"
    )

    print()

    # ----------------------------------
    # AI EXPLANATION
    # ----------------------------------

    print("AI DECISION:")

    if critical_count == 0:

        print(
            "✓ Critical zones were avoided."
        )

    else:

        print(
            "⚠ Critical zone entered because "
            "it is the destination."
        )

    if dangerous_count <= 1:

        print(
            "✓ Dangerous exposure was minimized."
        )

    else:

        print(
            "⚠ Route contains multiple "
            "dangerous cells."
        )

    if safe_count > caution_count:

        print(
            "✓ AI strongly preferred safer terrain."
        )

    else:

        print(
            "→ Route required significant "
            "caution zones."
        )

    print()
    print(
        "Final strategy: "
        "Minimize environmental risk while "
        "maintaining a feasible route."
    )

    print()
    print("--------------------------------------")

    print(
        f"Total Route Cost: "
        f"{total_cost:.2f}"
    )

    print("--------------------------------------")


# --------------------------------------
# RUN
# --------------------------------------

if __name__ == "__main__":
    main()