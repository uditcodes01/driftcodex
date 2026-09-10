# --------------------------------------
# LUNAR CODEX - RISK MODEL
# --------------------------------------


def calculate_risk(ice_risk, weather_risk, hazard_risk):
    """
    Calculate the overall environmental risk.
    """

    risk = (
        ice_risk * 0.4
        + weather_risk * 0.3
        + hazard_risk * 0.3
    )

    return round(risk, 2)


# --------------------------------------
# DEMONSTRATION
# --------------------------------------

def main():

    ice = 40
    weather = 30
    hazard = 20

    risk = calculate_risk(
        ice,
        weather,
        hazard
    )

    print("LUNAR CODEX - Antarctic Navigation AI")
    print("--------------------------------------")
    print(f"Ice Risk: {ice}/100")
    print(f"Weather Risk: {weather}/100")
    print(f"Hazard Risk: {hazard}/100")
    print(f"Overall Route Risk: {risk}/100")


# --------------------------------------
# RUN ONLY WHEN FILE IS EXECUTED
# DIRECTLY
# --------------------------------------

if __name__ == "__main__":
    main()