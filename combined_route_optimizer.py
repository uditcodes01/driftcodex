# --------------------------------------
# LUNAR CODEX - AI ROUTE OPTIMIZER
# USING REAL COMBINED ENVIRONMENTAL RISK
# --------------------------------------

import heapq
import numpy as np

from combined_risk import combined_risk


ROWS = combined_risk.shape[0]
COLS = combined_risk.shape[1]


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
# FIND VALID NAVIGATION CELLS
# --------------------------------------

def find_valid_cells():

    cells = []

    for row in range(ROWS):

        for col in range(COLS):

            risk = combined_risk[row, col]

            if not np.isnan(risk):

                cells.append(
                    (row, col)
                )

    return cells


# --------------------------------------
# SELECT START + DESTINATION
# --------------------------------------

def choose_start_and_goal():

    valid_cells = find_valid_cells()

    if len(valid_cells) < 2:

        return None, None


    safe_cells = [

        cell

        for cell in valid_cells

        if combined_risk[cell] < 30

    ]


    if len(safe_cells) < 2:

        safe_cells = valid_cells


    # Choose a starting point
    # roughly in the lower-left region

    start = min(

        safe_cells,

        key=lambda cell: (
            abs(cell[0] - ROWS * 0.70)
            +
            abs(cell[1] - COLS * 0.25)
        )

    )


    # Find a destination far away
    # but still reachable

    candidates = [

        cell

        for cell in valid_cells

        if cell != start
    ]


    goal = max(

        candidates,

        key=lambda cell: (
            abs(cell[0] - start[0])
            +
            abs(cell[1] - start[1])
        )
        -
        combined_risk[cell] * 0.05

    )


    return start, goal


# --------------------------------------
# MOVEMENT COST
# --------------------------------------

def get_cost(position):

    risk = combined_risk[position]


    if np.isnan(risk):

        return float("inf")


    # Base movement cost
    distance_cost = 1


    # Environmental risk penalty
    risk_cost = risk * 0.5


    # Strongly discourage dangerous zones

    if risk >= 60:

        risk_cost = risk * 3


    return distance_cost + risk_cost


# --------------------------------------
# HEURISTIC
# --------------------------------------

def heuristic(position, goal):

    return (

        abs(position[0] - goal[0])

        +

        abs(position[1] - goal[1])

    )


# --------------------------------------
# NEIGHBORS
# --------------------------------------

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

            and

            0 <= new_col < COLS

        ):

            risk = combined_risk[
                new_row,
                new_col
            ]


            if not np.isnan(risk):

                neighbors.append(

                    (new_row, new_col)

                )


    return neighbors


# --------------------------------------
# A* ROUTE SEARCH
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

        _, current = heapq.heappop(

            priority_queue

        )


        if current == goal:

            break


        for neighbor in get_neighbors(

            current

        ):


            new_cost = (

                cost_so_far[current]

                +

                get_cost(neighbor)

            )


            if (

                neighbor not in cost_so_far

                or

                new_cost < cost_so_far[neighbor]

            ):


                cost_so_far[neighbor] = new_cost


                priority = (

                    new_cost

                    +

                    heuristic(

                        neighbor,

                        goal

                    )

                )


                heapq.heappush(

                    priority_queue,

                    (

                        priority,

                        neighbor

                    )

                )


                came_from[neighbor] = current


    # No route

    if goal not in cost_so_far:

        return None, None


    # Reconstruct route

    route = []

    current = goal


    while current != start:

        route.append(current)

        current = came_from[current]


    route.append(start)

    route.reverse()


    return (

        route,

        cost_so_far[goal]

    )


# --------------------------------------
# ROUTE ANALYSIS
# --------------------------------------

def analyze_route(route):

    risks = []

    safe = 0
    caution = 0
    dangerous = 0
    critical = 0


    for position in route:

        risk = combined_risk[position]

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


# --------------------------------------
# MAIN
# --------------------------------------

def main():

    print()

    print("======================================")

    print(" LUNAR CODEX - AI NAVIGATION")

    print("======================================")

    print()


    print(

        "Combined environmental grid:",

        ROWS,

        "x",

        COLS

    )


    print()

    print(

        "Risk model:"

    )

    print(

        "60% Ice Risk + 40% Weather Risk"

    )


    print()

    print("Risk levels:")

    print("0-30   = SAFE")

    print("30-60  = CAUTION")

    print("60-80  = DANGEROUS")

    print("80-100 = CRITICAL")


    print()


    # ----------------------------------
    # START + GOAL
    # ----------------------------------

    start, goal = choose_start_and_goal()


    if start is None:

        print(

            "ERROR: No valid navigation cells."

        )

        return


    print("======================================")

    print(" ENVIRONMENTAL ANALYSIS")

    print("======================================")

    print()


    print(

        "Valid navigation cells:",

        len(find_valid_cells())

    )


    print()


    print("START:", start)

    print(

        "Start risk:",

        round(

            float(combined_risk[start]),

            2

        )

    )

    print(

        "Start level:",

        get_risk_level(

            combined_risk[start]

        )

    )


    print()


    print("DESTINATION:", goal)

    print(

        "Destination risk:",

        round(

            float(combined_risk[goal]),

            2

        )

    )

    print(

        "Destination level:",

        get_risk_level(

            combined_risk[goal]

        )

    )


    print()


    # ----------------------------------
    # ROUTE
    # ----------------------------------

    print("======================================")

    print(" CALCULATING AI ROUTE")

    print("======================================")

    print()


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
    # ANALYSIS
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

    print(" AI OPTIMIZED ROUTE")

    print("======================================")

    print()


    print(

        "Route cells:",

        len(route)

    )


    print()


    print("First part of route:")


    for point in route[:10]:

        risk = combined_risk[point]

        print(

            f"{point} "

            f"Risk: {risk:.1f} "

            f"-> "

            f"{get_risk_level(risk)}"

        )


    print()

    print(".........................")

    print()

    print("Final part of route:")


    for point in route[-10:]:

        risk = combined_risk[point]

        print(

            f"{point} "

            f"Risk: {risk:.1f} "

            f"-> "

            f"{get_risk_level(risk)}"

        )


    # ----------------------------------
    # DECISION ANALYSIS
    # ----------------------------------

    print()

    print("======================================")

    print(" ROUTE DECISION ANALYSIS")

    print("======================================")

    print()


    print("SAFE cells:", safe)

    print("CAUTION cells:", caution)

    print("DANGEROUS cells:", dangerous)

    print("CRITICAL cells:", critical)


    print()


    print(

        "Average route risk:",

        round(

            float(average_risk),

            2

        )

    )


    print(

        "Maximum route risk:",

        round(

            float(maximum_risk),

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

            float(total_cost),

            2

        )

    )


    # ----------------------------------
    # AI DECISION
    # ----------------------------------

    print()

    print("======================================")

    print(" AI DECISION")

    print("======================================")

    print()


    if critical == 0:

        print(

            "✓ AI avoided critical zones."

        )

    else:

        print(

            "⚠ Route encountered critical zones."

        )


    if dangerous == 0:

        print(

            "✓ AI avoided dangerous zones."

        )

    else:

        print(

            "✓ AI minimized dangerous exposure."

        )


    if average_risk < 30:

        print(

            "✓ Route maintained low "

            "environmental risk."

        )

    elif average_risk < 60:

        print(

            "→ Route maintained moderate "

            "environmental risk."

        )

    else:

        print(

            "⚠ Route contains substantial "

            "environmental risk."

        )


    print()

    print("FINAL STRATEGY:")

    print(

        "Minimize environmental risk "

        "while maintaining a feasible route."

    )


    print()

    print("--------------------------------------")

    print(" REAL-DATA AI NAVIGATION READY 🚀")

    print("--------------------------------------")


if __name__ == "__main__":

    main()