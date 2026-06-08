import fastf1
import matplotlib.pyplot as plt
import pandas as pd

# Enable caching
fastf1.Cache.enable_cache('f1_cache')

# USER INPUT - Change these to analyze different races
YEAR = 2024
RACE = 'Monaco'  # Change this to any race name
SESSION_TYPE = 'Q'  # 'Q', 'R', 'FP1', 'FP2', 'FP3', 'SS', 'S'
DRIVERS = ['VER', 'LEC']  # Change drivers here

# Load session
print(f"Loading {RACE} {YEAR} {SESSION_TYPE}...")
session = fastf1.get_session(YEAR, RACE, SESSION_TYPE)
session.load()

# Get driver data
print(f"Extracting telemetry for {DRIVERS}...")
telemetries = {}
for driver in DRIVERS:
    lap = session.laps.pick_driver(driver).pick_fastest()
    telemetries[driver] = lap.get_telemetry()

# Plot comparison
plt.figure(figsize=(12, 6))
for driver, tel in telemetries.items():
    plt.plot(tel['Distance'], tel['Speed'], label=driver, linewidth=2)

plt.xlabel('Distance [m]')
plt.ylabel('Speed [km/h]')
plt.title(f'Speed Comparison - {RACE} {YEAR} {SESSION_TYPE}')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
filename = f'speed_{RACE}_{YEAR}_{SESSION_TYPE}.png'
plt.savefig(filename, dpi=300)
print(f"Saved: {filename}")
plt.show()