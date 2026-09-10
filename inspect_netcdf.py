import xarray as xr


file_path = "../data/sh_20230526.nc"

ds = xr.open_dataset(file_path)


print("======================================")
print("   LUNAR CODEX - NETCDF INSPECTION")
print("======================================")
print()

print("DATASET:")
print(ds)

print()
print("VARIABLES:")

for variable in ds.data_vars:
    print("-", variable)

print()
print("COORDINATES:")

for coordinate in ds.coords:
    print("-", coordinate)

print()
print("DIMENSIONS:")

for name, size in ds.sizes.items():
    print(f"- {name}: {size}")