import pandas as pd
import joblib
from bmkg_fetcher import fetch_bmkg_forecast
from preprocess import transform_preprocess



# ===================================================
# LOAD MODEL
# ===================================================
model = joblib.load("models/flood_xgb_model.pkl")



# ===================================================
# LOAD ADM MAPPING
# ===================================================
adm_map = pd.read_csv("data/AreaCodes.csv")

adm_map["kelurahan"] = (
    adm_map["kelurahan"]
    .str.lower()
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)

kelurahan_to_adm4 = dict(
    zip(adm_map["kelurahan"], adm_map["adm4"])
)




# ===================================================
# WEATHER → RAIN LEVEL
# ===================================================
def map_weather_to_rain_level(desc: str) -> int:
    d = desc.lower()
    if any(x in d for x in ["petir", "thunder", "badai"]):
        return 4
    if any(x in d for x in ["hujan lebat", "hujan deras"]):
        return 3
    if "hujan sedang" in d:
        return 2
    if any(x in d for x in ["hujan ringan", "gerimis"]):
        return 1
    return 0




# ===================================================
# MAIN PIPELINE
# ===================================================
def predict_flood_for_kelurahan(kelurahan_name: str, force_rain_level: int = None):

    kel = kelurahan_name.lower().strip()

    if kel not in kelurahan_to_adm4:
        raise ValueError(f"Kelurahan '{kelurahan_name}' not found in AreaCodes.csv")

    adm4_code = kelurahan_to_adm4[kel]

    data = fetch_bmkg_forecast(adm4_code)

    cuaca_blocks = data["data"][0]["cuaca"]
    forecast_slots = [slot for block in cuaca_blocks for slot in block]

    results = []

    for slot in forecast_slots:
        row = {
            "local_datetime": slot["local_datetime"],
            "subdistrict_name": kel,
            "adm4": adm4_code,
            "t": slot.get("t"),
            "hu": slot.get("hu"),
            "ws": slot.get("ws"),
            "wd": slot.get("wd_deg"),
            "tcc": slot.get("tcc"),
            "visibility": slot.get("vs_text"),
            "rain_level": (force_rain_level if force_rain_level is not None else map_weather_to_rain_level(slot["weather_desc"])),
            "sea_level": 0.5,
            "tide_height": 0.5,
        }

        X = transform_preprocess(pd.DataFrame([row]))

        pred = model.predict(X)[0]
        prob = model.predict_proba(X)[0][1]

        results.append({
            "datetime": row["local_datetime"],
            "weather": slot["weather_desc"],
            "temperature": slot.get("t"),
            "humidity": slot.get("hu"),
            "flood_prediction": int(pred),
            "probability": float(prob * 100)
        })

    return results
