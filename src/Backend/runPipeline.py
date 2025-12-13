from flood_pipeline import predict_flood_for_kelurahan

kelurahan = "kalideres"
results = predict_flood_for_kelurahan(kelurahan)

print("\n================ FLOOD PREDICTION RESULT ================\n")
print(f" Kelurahan : {kelurahan.title()}")
print("----------------------------------------------------------\n")

for idx, r in enumerate(results, start=1):
    print(f"Forecast {idx}:")
    print(f"  Date/Time       : {r['datetime']}")
    print(f"  Weather         : {r['weather']}")
    print(f"  Temperature     : {r['temperature']} C")
    print(f"  humidity        : {r['humidity']}")
    print(f"  Flood Predicted : {'YES' if r['flood_prediction'] == 1 else 'NO'}")
    print(f"  Flood Prob      : {r['probability']:.1f}%")
    print("----------------------------------------------------------\n")

print("======================== END ============================\n")
