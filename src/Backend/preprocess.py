import pandas as pd

def fit_preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ---------------------------
    # Normalize kelurahan
    # ---------------------------
    df["subdistrict_name"] = (
        df["subdistrict_name"]
        .str.lower()
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # ---------------------------
    # ADM4 → numeric (stable)
    # ---------------------------
    df["adm4"] = df["adm4"].astype("category").cat.codes

    # ---------------------------
    # Datetime features
    # ---------------------------
    df["local_datetime"] = pd.to_datetime(df["local_datetime"])
    df["hour"] = df["local_datetime"].dt.hour
    df["day"] = df["local_datetime"].dt.day
    df["month"] = df["local_datetime"].dt.month

    # ---------------------------
    # Wind direction
    # ---------------------------
    if df["wd"].dtype == object:
        df["wd"] = df["wd"].astype("category").cat.codes

    # ---------------------------
    # Numeric safety
    # ---------------------------
    numeric_cols = [
        "t", "hu", "ws", "tcc", "visibility",
        "rain_level", "sea_level", "tide_height"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ---------------------------
    # Drop text columns
    # ---------------------------
    df = df.drop(columns=[
        "local_datetime",
        "subdistrict_name",
        "weather_desc_en"
    ], errors="ignore")

    return df


def transform_preprocess(df: pd.DataFrame) -> pd.DataFrame:
    return fit_preprocess(df)
