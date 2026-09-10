# --------------------------------------
# LUNAR CODEX - REAL ANTARCTIC ICE RISK
# --------------------------------------

import xarray as xr
import numpy as np


# --------------------------------------
# LOAD REAL ANTARCTIC DATA
# --------------------------------------

FILE_PATH = "../data/sh_20230526.nc"

ds = xr.open_dataset(FILE_PATH)

ice_data = ds["tc_mid"].values[0]


# --------------------------------------
# CREATE ICE RISK
# --------------------------------------

def calculate_ice_risk(ice_data):

    ice_risk = np.full(
        ice_data.shape,
        np.nan,
        dtype=np.float32
    )

    # ----------------------------------
    # REAL ICE CONCENTRATION
    # 0-100%
    # ----------------------------------

    real_ice = (
        (ice_data >= 0)
        & (ice_data <= 100)
    )

    ice_risk[real_ice] = ice_data[real_ice]


    # ----------------------------------
    # FAST ICE
    # ----------------------------------

    fast_ice = ice_data == 110

    ice_risk[fast_ice] = 100


    # ----------------------------------
    # USUALLY OCEAN
    # ----------------------------------

    usually_ocean = ice_data == 118

    ice_risk[usually_ocean] = 0


    # ----------------------------------
    # LAND
    # Keep as NaN = NOT ROUTABLE
    # ----------------------------------

    land = ice_data == 119

    ice_risk[land] = np.nan


    # ----------------------------------
    # UNKNOWN / OTHER SPECIAL FLAGS
    # ----------------------------------

    special_values = (
        (ice_data > 100)
        & (ice_data != 110)
        & (ice_data != 118)
        & (ice_data != 119)
    )

    ice_risk[special_values] = np.nan


    return ice_risk


# --------------------------------------
# GENERATE ICE RISK
# --------------------------------------

ice_risk = calculate_ice_risk(
    ice_data
)


# --------------------------------------
# MAIN
# --------------------------------------

if __name__ == "__main__":

    print("======================================")
    print("   LUNAR CODEX - REAL ICE RISK")
    print("======================================")
    print()

    print("Dataset:")
    print("USNIC Antarctic Ice Data")

    print()

    print("Date:")
    print("2023-05-26")

    print()

    print("Grid:")
    print(
        f"{ice_risk.shape[0]} x "
        f"{ice_risk.shape[1]}"
    )

    print()

    print("Real Antarctic ice data loaded!")

    print()

    print(
        "Minimum raw value:",
        ice_data.min()
    )

    print(
        "Maximum raw value:",
        ice_data.max()
    )

    print(
        "Land cells:",
        np.sum(ice_data == 119)
    )

    print(
        "Ocean cells:",
        np.sum(ice_data == 118)
    )

    print()

    print(
        "Ice risk array created successfully!"
    )

    print()

    print("Sample risk values:")

    print(
        ice_risk[500:505, 500:505]
    )

    print()

    print("--------------------------------------")
    print("REAL ANTARCTIC ICE RISK READY 🚀")
    print("--------------------------------------")