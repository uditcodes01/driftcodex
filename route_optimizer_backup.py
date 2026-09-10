from risk_grid import risk_grid
import heapq


# Grid dimensions
ROWS = len(risk_grid)
COLS = len(risk_grid[0])


# Calculate movement cost
def get_cost(position):

    row, col = position
    risk = risk_grid[row][col]

    # Distance cost
    distance_cost = 1

    # Environmental risk cost
    risk_cost = risk * 0.5

    # Strong penalty for extremely dangerous areas
    if risk >= 60:
        risk_cost = risk * 3

    return distance_cost + risk_cost


# Manhattan distance heuristic
def heuristic(position, goal):

    row, col = position

    return abs(row - goal[0]) + abs(col - goal[1])


# Find neighbouring cells
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


# A* route-finding algorithm
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

        current_priority, current = heapq.heappop(priority_queue)

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
                    + heuristic(neighbor, goal)
                )

                heapq.heappush(
                    priority_queue,
                    (priority, neighbor)
                )

                came_from[neighbor] = current


    # Reconstruct route
    route = []

    current = goal

    while current != start:

        route.append(current)
        current = came_from[current]

    route.append(start)

    route.reverse()

    return route, cost_so_far[goal]


# Interactive program
def main():

    print()
    print("======================================")
    print("   LUNAR CODEX - ROUTE OPTIMIZER")
    print("======================================")
    print()

    print("Grid size:", ROWS, "rows x", COLS, "columns")

    print()
    print("Available coordinates:")
    print("(row, column)")
    print()

    # Ask user for start
    start_row = int(input("Enter START row (0-3): "))
    start_col = int(input("Enter START column (0-4): "))

    start = (start_row, start_col)

    # Ask user for destination
    goal_row = int(input("Enter DESTINATION row (0-3): "))
    goal_col = int(input("Enter DESTINATION column (0-4): "))

    goal = (goal_row, goal_col)

    # Calculate route
    route, total_cost = find_route(start, goal)

    # Display route
    print()
    print("AI OPTIMIZED ROUTE")
    print("------------------")

    for position in route:

        row, col = position

        print(
            f"{position} "
            f"Risk: {risk_grid[row][col]}"
        )

    print()
    print(f"Total Route Cost: {total_cost:.2f}")


# Run interactive program
if __name__ == "__main__":
    main()