from risk_model import calculate_risk


# Antarctic environmental conditions
# Each location contains:
# ice risk, weather risk, hazard risk

locations = [
    (20, 15, 10),
    (25, 20, 15),
    (30, 25, 20),
    (80, 70, 60),
    (90, 80, 70),

    (15, 10, 10),
    (20, 20, 15),
    (35, 30, 25),
    (70, 65, 60),
    (85, 75, 70),

    (10, 10, 5),
    (15, 15, 10),
    (25, 20, 15),
    (40, 35, 30),
    (60, 50, 45),

    (20, 15, 10),
    (25, 20, 15),
    (20, 15, 10),
    (30, 25, 20),
    (45, 35, 30)
]


# Create the risk grid
risk_grid = []

for location in locations:

    ice, weather, hazard = location

    risk = calculate_risk(
        ice,
        weather,
        hazard
    )

    risk_grid.append(risk)


# Convert into 4 rows × 5 columns
risk_grid = [
    risk_grid[0:5],
    risk_grid[5:10],
    risk_grid[10:15],
    risk_grid[15:20]
]


if __name__ == "__main__":

    print("LUNAR CODEX - ANTARCTIC RISK GRID")
    print("----------------------------------")

    for row in risk_grid:
        print(row)