from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import heapq
import os

app = Flask(__name__)
CORS(app)

# ============================================================
# DRIFTCODEX — ADAPTIVE RISK-AWARE A* ROUTING BACKEND
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")

RISK_FILE = os.path.join(DATA_DIR, "total_risk_20230526.npy")

START = (402, 490)
DESTINATION = (501, 51)

BASELINE_RISK = 7.04

ICE_WEIGHT = 0.40
WEATHER_WEIGHT = 0.30
HAZARD_WEIGHT = 0.30


# ============================================================
# LOAD BASE RISK GRID
# ============================================================

if not os.path.exists(RISK_FILE):
    raise FileNotFoundError(
        f"Risk grid not found: {RISK_FILE}"
    )

BASE_RISK_GRID = np.load(RISK_FILE).astype(float)

print("DRIFTCODEX BACKEND")
print("------------------")
print("Risk grid:", BASE_RISK_GRID.shape)
print("Start:", START)
print("Destination:", DESTINATION)


# ============================================================
# RISK-AWARE COST
# ============================================================

def risk_cost(risk):

    if not np.isfinite(risk):
        return np.inf

    if risk >= 80:
        return np.inf

    if risk >= 60:
        return 1 + risk * 8

    if risk >= 30:
        return 1 + risk * 2

    return 1 + risk * 0.3


# ============================================================
# A* HEURISTIC
# ============================================================

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ============================================================
# RISK-AWARE A*
# ============================================================

def astar(risk_grid, start, goal):

    rows, cols = risk_grid.shape

    open_set = []

    heapq.heappush(
        open_set,
        (0, start)
    )

    came_from = {}

    g_score = {
        start: 0
    }

    visited = set()

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    while open_set:

        _, current = heapq.heappop(open_set)

        if current in visited:
            continue

        visited.add(current)

        if current == goal:

            path = []

            while current in came_from:
                path.append(current)
                current = came_from[current]

            path.append(start)
            path.reverse()

            return path, g_score[goal]

        r, c = current

        for dr, dc in directions:

            nr = r + dr
            nc = c + dc

            if nr < 0 or nr >= rows:
                continue

            if nc < 0 or nc >= cols:
                continue

            neighbor = (nr, nc)

            cell_risk = risk_grid[nr, nc]

            movement_cost = risk_cost(cell_risk)

            if not np.isfinite(movement_cost):
                continue

            tentative_g = (
                g_score[current] +
                movement_cost
            )

            if (
                neighbor not in g_score
                or tentative_g < g_score[neighbor]
            ):

                came_from[neighbor] = current

                g_score[neighbor] = tentative_g

                f_score = (
                    tentative_g +
                    heuristic(neighbor, goal)
                )

                heapq.heappush(
                    open_set,
                    (f_score, neighbor)
                )

    return None, None


# ============================================================
# ROUTE STATISTICS
# ============================================================

def calculate_route_stats(route, risk_grid):

    if not route:
        return None

    route_risks = np.array(
        [risk_grid[r, c] for r, c in route]
    )

    average_risk = float(np.mean(route_risks))
    maximum_risk = float(np.max(route_risks))

    dangerous = int(
        np.sum(
            (route_risks >= 60) &
            (route_risks < 80)
        )
    )

    critical = int(
        np.sum(route_risks >= 80)
    )

    caution = int(
        np.sum(
            (route_risks >= 30) &
            (route_risks < 60)
        )
    )

    safe = int(
        np.sum(route_risks < 30)
    )

    return {
        "route_cells": len(route),
        "average_risk": round(average_risk, 2),
        "maximum_risk": round(maximum_risk, 2),
        "safe_cells": safe,
        "caution_cells": caution,
        "dangerous_cells": dangerous,
        "critical_cells": critical
    }


# ============================================================
# JSON ROUTE CONVERSION
# ============================================================

def route_to_coordinates(route):

    if not route:
        return []

    return [
        {
            "row": int(r),
            "col": int(c)
        }
        for r, c in route
    ]


# ============================================================
# BASELINE ROUTE
# ============================================================

print()
print("Calculating baseline route...")

BASELINE_ROUTE, BASELINE_ROUTE_COST = astar(
    BASE_RISK_GRID,
    START,
    DESTINATION
)

if BASELINE_ROUTE is None:
    raise RuntimeError(
        "Baseline A* route could not be calculated."
    )

BASELINE_STATS = calculate_route_stats(
    BASELINE_ROUTE,
    BASE_RISK_GRID
)

print(
    "Baseline route cells:",
    len(BASELINE_ROUTE)
)

print(
    "Baseline average risk:",
    BASELINE_STATS["average_risk"]
)


# ============================================================
# CREATE SIMULATED ENVIRONMENT
# ============================================================

def create_simulated_grid(
    ice_change,
    weather_change,
    hazard_change
):

    combined_change = (
        ICE_WEIGHT * ice_change +
        WEATHER_WEIGHT * weather_change +
        HAZARD_WEIGHT * hazard_change
    )

    multiplier = 1 + (
        combined_change / 100.0
    )

    multiplier = max(
        0.05,
        multiplier
    )

    simulated_grid = (
        BASE_RISK_GRID *
        multiplier
    )

    simulated_grid = np.clip(
        simulated_grid,
        0,
        100
    )

    return simulated_grid


# ============================================================
# ROUTE CHANGE DETECTION
# ============================================================

def compare_routes(old_route, new_route):

    if not old_route or not new_route:
        return {
            "route_changed": False,
            "common_cells": 0,
            "changed_cells": 0,
            "change_percentage": 0
        }

    old_set = set(old_route)
    new_set = set(new_route)

    common_cells = len(
        old_set.intersection(new_set)
    )

    changed_cells = len(
        old_set.symmetric_difference(new_set)
    )

    reference_size = max(
        len(old_set),
        len(new_set),
        1
    )

    change_percentage = (
        changed_cells /
        reference_size
    ) * 100

    return {
        "route_changed": old_route != new_route,
        "common_cells": common_cells,
        "changed_cells": changed_cells,
        "change_percentage": round(
            change_percentage,
            2
        )
    }


# ============================================================
# SIMULATION API
# ============================================================

@app.route(
    "/simulate",
    methods=["POST"]
)
def simulate():

    try:

        data = request.get_json(
            force=True
        )

        ice_change = float(
            data.get(
                "ice_change",
                0
            )
        )

        weather_change = float(
            data.get(
                "weather_change",
                0
            )
        )

        hazard_change = float(
            data.get(
                "hazard_change",
                0
            )
        )

        # ----------------------------------------------------
        # LIMIT USER INPUT
        # ----------------------------------------------------

        ice_change = float(
            np.clip(
                ice_change,
                -50,
                50
            )
        )

        weather_change = float(
            np.clip(
                weather_change,
                -50,
                50
            )
        )

        hazard_change = float(
            np.clip(
                hazard_change,
                -50,
                50
            )
        )

        # ----------------------------------------------------
        # CREATE CHANGED RISK ENVIRONMENT
        # ----------------------------------------------------

        simulated_grid = create_simulated_grid(
            ice_change,
            weather_change,
            hazard_change
        )

        # ----------------------------------------------------
        # RUN A* AGAIN
        # ----------------------------------------------------

        simulated_route, route_cost = astar(
            simulated_grid,
            START,
            DESTINATION
        )

        # ----------------------------------------------------
        # NO ROUTE
        # ----------------------------------------------------

        if simulated_route is None:

            return jsonify({
                "success": False,
                "message": (
                    "No safe route could be found "
                    "under the simulated conditions."
                )
            }), 200

        # ----------------------------------------------------
        # NEW ROUTE STATS
        # ----------------------------------------------------

        stats = calculate_route_stats(
            simulated_route,
            simulated_grid
        )

        # ----------------------------------------------------
        # SIMULATED OVERALL RISK
        # ----------------------------------------------------

        combined_change = (
            ICE_WEIGHT * ice_change +
            WEATHER_WEIGHT * weather_change +
            HAZARD_WEIGHT * hazard_change
        )

        simulated_risk = (
            BASELINE_RISK *
            (
                1 +
                combined_change / 100
            )
        )

        simulated_risk = float(
            np.clip(
                simulated_risk,
                0,
                100
            )
        )

        risk_change = (
            simulated_risk -
            BASELINE_RISK
        )

        percentage_change = (
            (
                risk_change /
                BASELINE_RISK
            ) * 100
            if BASELINE_RISK != 0
            else 0
        )

        # ----------------------------------------------------
        # COMPARE OLD VS NEW ROUTE
        # ----------------------------------------------------

        route_comparison = compare_routes(
            BASELINE_ROUTE,
            simulated_route
        )

        # ----------------------------------------------------
        # DECISION LOGIC
        # ----------------------------------------------------

        if stats["critical_cells"] > 0:

            status = "CRITICAL"

            decision = (
                "CRITICAL — REROUTE REQUIRED"
            )

            decision_text = (
                "Critical-risk cells are present. "
                "The A* engine selected the lowest-risk "
                "available corridor."
            )

        elif stats["dangerous_cells"] > 0:

            status = "REROUTE"

            decision = (
                "REROUTE RECOMMENDED"
            )

            decision_text = (
                "The environment has degraded enough "
                "to introduce dangerous cells. "
                "The A* engine has recalculated the "
                "lowest-risk available corridor."
            )

        elif simulated_risk >= 30:

            status = "CAUTION"

            decision = (
                "CAUTION — MONITOR CONDITIONS"
            )

            decision_text = (
                "Environmental risk has increased. "
                "The navigation corridor remains available "
                "but should be monitored."
            )

        else:

            status = "STABLE"

            decision = (
                "CORRIDOR STABLE"
            )

            decision_text = (
                "The Python risk engine recalculated "
                "the environment and A* still found "
                "a low-risk navigation corridor."
            )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return jsonify({

            "success": True,

            "simulation": {

                "baseline_risk": round(
                    BASELINE_RISK,
                    2
                ),

                "simulated_risk": round(
                    simulated_risk,
                    2
                ),

                "risk_change": round(
                    risk_change,
                    2
                ),

                "percentage_change": round(
                    percentage_change,
                    2
                ),

                "status": status,

                "decision": decision,

                "decision_text": decision_text,

                "ice_change": ice_change,

                "weather_change": weather_change,

                "hazard_change": hazard_change,

                "combined_change": round(
                    combined_change,
                    2
                )
            },

            "adaptive_routing": {

                "route_changed": (
                    route_comparison[
                        "route_changed"
                    ]
                ),

                "common_cells": (
                    route_comparison[
                        "common_cells"
                    ]
                ),

                "changed_cells": (
                    route_comparison[
                        "changed_cells"
                    ]
                ),

                "change_percentage": (
                    route_comparison[
                        "change_percentage"
                    ]
                ),

                "message": (
                    "A* recalculated the "
                    "navigation corridor."
                    if route_comparison[
                        "route_changed"
                    ]
                    else
                    "Current corridor remains "
                    "the lowest-risk available route."
                )
            },

            "baseline_route": {

                "start": {
                    "row": START[0],
                    "col": START[1]
                },

                "destination": {
                    "row": DESTINATION[0],
                    "col": DESTINATION[1]
                },

                "cost": round(
                    float(
                        BASELINE_ROUTE_COST
                    ),
                    2
                ),

                "coordinates": route_to_coordinates(
                    BASELINE_ROUTE
                ),

                **BASELINE_STATS
            },

            "route": {

                "start": {
                    "row": START[0],
                    "col": START[1]
                },

                "destination": {
                    "row": DESTINATION[0],
                    "col": DESTINATION[1]
                },

                "cost": round(
                    float(route_cost),
                    2
                ),

                "coordinates": route_to_coordinates(
                    simulated_route
                ),

                **stats
            }

        })

    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/",
    methods=["GET"]
)
def home():

    return jsonify({

        "system": "DRIFTCODEX",

        "status": "ONLINE",

        "engine": "Risk-Aware A*",

        "mode": "Adaptive Routing",

        "endpoint": "/simulate"

    })


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("======================================")
    print(" DRIFTCODEX AI ROUTING SERVER")
    print("======================================")
    print(
        "Server: http://127.0.0.1:5000"
    )
    print(
        "API:    http://127.0.0.1:5000/simulate"
    )
    print()
    print(
        "Adaptive A* routing: READY"
    )
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )