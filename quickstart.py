import fastf1

fastf1.Cache.enable_cache('f1_cache')
session = fastf1.get_session(2023, 'Bahrain', 'Q')
session.load()

laps = session.laps.pick_driver('VER')
fastest = laps.pick_fastest()
telemetry = fastest.get_telemetry()

print("Telemetry columns:", telemetry.columns.tolist())
print("Success!")
