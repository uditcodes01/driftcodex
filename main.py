from risk_model import calculate_risk


print("======================================")
print("     LUNAR CODEX - AI NAVIGATION")
print("======================================")

ice = 40
weather = 30
hazard = 20

risk = calculate_risk(ice, weather, hazard)

print()
print(f"Ice Risk: {ice}/100")
print(f"Weather Risk: {weather}/100")
print(f"Hazard Risk: {hazard}/100")
print(f"Overall Route Risk: {risk}/100")