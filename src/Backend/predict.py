import pandas as pd
import joblib
from preprocess import transform_preprocess

# ===================================================
# LOAD TRAINED MODEL
# ===================================================
model = joblib.load("models/flood_xgb_model.pkl")


# ===================================================
# INPUT CLEANING (match training exactly)
# ===================================================
def clean_input(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalize kelurahan text (even if later dropped)
    if "subdistrict_name" in df.columns:
        df["subdistrict_name"] = (
            df["subdistrict_name"]
            .str.lower()
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    # Numeric safety
    numeric_cols = [
        "t", "hu", "ws", "tcc",
        "visibility", "rain_level",
        "sea_level", "tide_height"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ===================================================
# PREDICTION FUNCTION
# ===================================================
def predict_flood(input_df: pd.DataFrame):
    """
    Takes raw feature DataFrame and returns:
    - prediction (0/1)
    - probability (float)
    """

    # 1️⃣ Clean raw input
    input_df = clean_input(input_df)

    # 2️⃣ Apply SAME preprocess as training
    X = transform_preprocess(input_df)

    # 3️⃣ Predict
    prediction = model.predict(X)
    probability = model.predict_proba(X)[:, 1]

    return prediction, probability


# ===================================================
# MANUAL TEST
# ===================================================
if __name__ == "__main__":
    sample = pd.DataFrame([{
        "adm4": "31.73.06.1004",        # STRING is OK
        "local_datetime": "2024-01-02 15:00:00",
        "subdistrict_name": "kembangan utara",
        "t": 30,
        "hu": 95,
        "ws": 20,
        "wd": 135,                      # degrees (not text)
        "tcc": 95,
        "visibility": 1000,
        "rain_level": 3,
        "sea_level": 0.5,
        "tide_height": 0.2,
    }])

    pred, prob = predict_flood(sample)
    print(f"Flood prediction: {int(pred[0])}")
    print(f"Confidence      : {prob[0] * 100:.1f}%")
