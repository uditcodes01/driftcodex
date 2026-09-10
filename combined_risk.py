# --------------------------------------
# LUNAR CODEX - COMBINED ENVIRONMENTAL
# RISK MODEL
# --------------------------------------

import numpy as np

from ice_risk import ice_risk
from weather_risk import weather_risk


# --------------------------------------
# ALIGN BOTH DATASETS
# --------------------------------------

# Ice data is 1050 x 1050
# Weather data is 161 x 1440
#
# For the first prototype we use a
# common 105 x 105 navigation grid.

SCALE = 10

ice_grid = ice_risk[::SCALE, ::SCALE]


# --------------------------------------
# RESIZE WEATHER DATA
# --------------------------------------

weather_rows = np.linspace(
    0,
    weather_risk.shape[0] - 1,
    ice_grid.shape[0]
).astype(int)

weather_cols = np.linspace(
    0,
    weather_risk.shape[1] - 1,
    ice_grid.shape[1]
).astype(int)


weather_grid = weather_risk[
    np.ix_(
        weather_rows,
        weather_cols
    )
]


# --------------------------------------
# COMBINE ICE + WEATHER RISK
# --------------------------------------

combined_risk = np.full(
    ice_grid.shape,
    np.nan,
    dtype=np.float32
)


valid_cells = (
    ~np.isnan(ice_grid)
)


# Ice = 60%
# Weather = 40%

combined_risk[valid_cells] = (
    ice_grid[valid_cells] * 0.60
    + weather_grid[valid_cells] * 0.40
)


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
# ANALYSIS
# --------------------------------------

if __name__ == "__main__":

    valid = combined_risk[
        ~np.isnan(combined_risk)
    ]

    print()
    print("======================================")
    print(" LUNAR CODEX - COMBINED RISK MODEL")
    print("======================================")
    print()

    print("ICE DATA:")
    print(
        "Grid:",
        ice_grid.shape
    )

    print(
        "Weight:",
        "60%"
    )

    print()

    print("WEATHER DATA:")
    print(
        "Original grid:",
        weather_risk.shape
    )

    print(
        "Resampled grid:",
        weather_grid.shape
    )

    print(
        "Weight:",
        "40%"
    )

    print()

    print("======================================")
    print("       COMBINED RISK ANALYSIS")
    print("======================================")

    print()

    print(
        "Minimum risk:",
        round(
            float(np.nanmin(valid)),
            2
        )
    )

    print(
        "Maximum risk:",
        round(
            float(np.nanmax(valid)),
            2
        )
    )

    print(
        "Average risk:",
        round(
            float(np.nanmean(valid)),
            2
        )
    )

    print()

    print(
        "SAFE cells:",
        np.sum(
            (valid < 30)
        )
    )

    print(
        "CAUTION cells:",
        np.sum(
            (valid >= 30)
            & (valid < 60)
        )
    )

    print(
        "DANGEROUS cells:",
        np.sum(
            (valid >= 60)
            & (valid < 80)
        )
    )

    print(
        "CRITICAL cells:",
        np.sum(
            valid >= 80
        )
    )

    print()

    print("--------------------------------------")
    print(" COMBINED ENVIRONMENTAL RISK READY 🚀")
    print("--------------------------------------")