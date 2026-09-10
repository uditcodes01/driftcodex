# DRIFTCODEX - WHAT-IF ENVIRONMENT SIMULATOR

BASELINE_RISK = 7.04

ICE_WEIGHT = 0.40
WEATHER_WEIGHT = 0.30
HAZARD_WEIGHT = 0.30


def calculate_simulated_risk(ice_change, weather_change, hazard_change):

    ice_factor = 1 + (ice_change / 100)
    weather_factor = 1 + (weather_change / 100)
    hazard_factor = 1 + (hazard_change / 100)

    baseline_ice = BASELINE_RISK * ICE_WEIGHT
    baseline_weather = BASELINE_RISK * WEATHER_WEIGHT
    baseline_hazard = BASELINE_RISK * HAZARD_WEIGHT

    simulated_ice = baseline_ice * ice_factor
    simulated_weather = baseline_weather * weather_factor
    simulated_hazard = baseline_hazard * hazard_factor

    simulated_risk = (
        simulated_ice +
        simulated_weather +
        simulated_hazard
    )

    return max(0, min(100, simulated_risk))


def classify_risk(risk):

    if risk < 30:
        return "STABLE"
    elif risk < 60:
        return "CAUTION"
    elif risk < 80:
        return "REROUTE RECOMMENDED"
    else:
        return "CRITICAL - REROUTE"


def run_simulation(ice_change, weather_change, hazard_change):

    simulated_risk = calculate_simulated_risk(
        ice_change,
        weather_change,
        hazard_change
    )

    change = simulated_risk - BASELINE_RISK

    percentage_change = (
        (change / BASELINE_RISK) * 100
        if BASELINE_RISK != 0
        else 0
    )

    return {
        "baseline_risk": round(BASELINE_RISK, 2),
        "simulated_risk": round(simulated_risk, 2),
        "risk_change": round(change, 2),
        "percentage_change": round(percentage_change, 2),
        "status": classify_risk(simulated_risk)
    }


if __name__ == "__main__":

    print("=" * 55)
    print("     DRIFTCODEX - WHAT-IF ENVIRONMENT SIMULATOR")
    print("=" * 55)

    # Test scenario
    ice_change = 20
    weather_change = 10
    hazard_change = 30

    result = run_simulation(
        ice_change,
        weather_change,
        hazard_change
    )

    print(f"\nBaseline Risk  : {result['baseline_risk']}/100")
    print(f"Simulated Risk : {result['simulated_risk']}/100")
    print(f"Risk Change    : {result['risk_change']:+}/100")
    print(f"Percentage     : {result['percentage_change']:+}%")
    print(f"Status         : {result['status']}")

    print("\nSimulation complete.")