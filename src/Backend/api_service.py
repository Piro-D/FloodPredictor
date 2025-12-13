import pandas as pd
import difflib
import unicodedata
import re
from pathlib import Path
import json

ADM_TABLE = pd.read_csv("data/AreaCodes.csv")

def _normalize_name(s: str) -> str:
    if not s:
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def get_adm4_from_kelurahan(kelurahan_name: str):
    """
    Accepts either a kelurahan name or an adm4 code.
    Tries exact (case-insensitive), normalized exact, then fuzzy match.
    Raises ValueError with suggestions if not found.
    """
    if not kelurahan_name:
        raise ValueError("Empty kelurahan/adm4 provided")

    val = str(kelurahan_name).strip()

    # direct adm4 match (digits/dots)
    if re.match(r'^[0-9.\-]+$', val):
        adm_mask = ADM_TABLE["adm4"].astype(str) == val
        if adm_mask.any():
            return ADM_TABLE.loc[adm_mask, "adm4"].iloc[0]

    # exact case-insensitive match on kelurahan column
    mask = ADM_TABLE["kelurahan"].str.lower() == val.lower()
    if mask.any():
        return ADM_TABLE.loc[mask, "adm4"].iloc[0]

    # normalized exact match
    input_norm = _normalize_name(val)
    norm_series = ADM_TABLE["kelurahan"].fillna("").apply(_normalize_name)
    norm_mask = norm_series == input_norm
    if norm_mask.any():
        return ADM_TABLE.loc[norm_mask, "adm4"].iloc[0]

    # fuzzy match on normalized names
    candidates = norm_series.tolist()
    match = difflib.get_close_matches(input_norm, candidates, n=1, cutoff=0.65)
    if match:
        idx = norm_series[norm_series == match[0]].index[0]
        return ADM_TABLE.loc[idx, "adm4"]

    # suggestions for error message
    suggestions = difflib.get_close_matches(input_norm, candidates, n=5, cutoff=0.45)
    suggestion_text = ", ".join({ADM_TABLE.loc[norm_series == s, "kelurahan"].iloc[0] for s in suggestions}) if suggestions else ""
    raise ValueError(f"Kelurahan {kelurahan_name!r} not found in ADM table. Suggestions: {suggestion_text}")

# --- ADD: lightweight Flask endpoint that uses existing pipeline ---
from flask import Flask, request, jsonify
from flask_cors import CORS

# import backend pipeline function (already in repo)
from flood_pipeline import predict_flood_for_kelurahan

app = Flask(__name__)
CORS(app)

@app.route("/predict", methods=["POST"])
def predict_route():
    payload = request.get_json(silent=True) or {}
    kelurahan_in = payload.get("kelurahan") or payload.get("subdistrict") or payload.get("subdistrict_name")
    if not kelurahan_in:
        return jsonify({"error": "Missing 'kelurahan' / 'subdistrict' field"}), 400

    try:
        # resolve to adm4 (accepts name or adm4) and get canonical kelurahan from ADM_TABLE
        adm4 = get_adm4_from_kelurahan(kelurahan_in)
        row = ADM_TABLE[ADM_TABLE["adm4"].astype(str) == str(adm4)].iloc[0]
        canonical_kelurahan = row["kelurahan"]
        print(f"Resolved {kelurahan_in!r} -> canonical {canonical_kelurahan!r}, adm4={adm4}", flush=True)

        # call pipeline with canonical kelurahan
        results = predict_flood_for_kelurahan(canonical_kelurahan.lower())

    except ValueError as e:
        # lookup failure or suggestions — return 400 so client can fix input
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Normalize results to JSON-serializable form
    safe = []
    for r in results:
        safe.append({
            "datetime": str(r.get("datetime")),
            "weather": r.get("weather"),
            "temperature": r.get("temperature"),
            "humidity": r.get("humidity"),
            "flood_prediction": int(r.get("flood_prediction")) if r.get("flood_prediction") is not None else None,
            "probability": float(r.get("probability")) if r.get("probability") is not None else None,
        })

    return jsonify({"kelurahan": canonical_kelurahan, "adm4": adm4, "results": safe}), 200

def _detect_columns(df):
    cols = {c.lower(): c for c in df.columns}
    def find(candidates):
        for cand in candidates:
            for k, orig in cols.items():
                if cand in k:
                    return orig
        return None
    return {
        "province": find(["prov", "province"]),
        "city": find(["kab", "city", "regency", "kabupaten", "kota"]),
        "district": find(["kec", "district", "kecamatan"]),
        "kelurahan": find(["kel", "kelurahan", "village", "subdistrict"]),
        "adm4": find(["adm4", "adm_4", "adm4_code"])
    }

@app.route("/areas", methods=["GET"])
def areas_route():
    """
    Return hierarchical area structure derived from data/AreaCodes.csv.
    Response JSON:
    { "provinceList": [ { province, cities: [ { city, districts: [ { district, subdistricts: [ { name, adm4 } ] } ] } ] } ] }
    """
    try:
        cols = _detect_columns(ADM_TABLE)
        if not cols["kelurahan"] or not cols["adm4"]:
            # fallback: return raw table if detection failed
            return jsonify({"error": "AreaCodes.csv missing expected columns", "columns": list(ADM_TABLE.columns)}), 500

        tree = {}
        for _, row in ADM_TABLE.iterrows():
            prov = row.get(cols["province"], "") or ""
            city = row.get(cols["city"], "") or ""
            dist = row.get(cols["district"], "") or ""
            kel = row.get(cols["kelurahan"], "") or ""
            adm4 = row.get(cols["adm4"], "")
            prov_k = str(prov).strip()
            city_k = str(city).strip()
            dist_k = str(dist).strip()
            kel_k = str(kel).strip()

            tree.setdefault(prov_k, {})
            tree[prov_k].setdefault(city_k, {})
            tree[prov_k][city_k].setdefault(dist_k, {})
            # store list of objects with name and adm4
            lst = tree[prov_k][city_k][dist_k].setdefault("subdistricts", [])
            # avoid duplicates
            if not any(x.get("name") == kel_k for x in lst):
                lst.append({"name": kel_k, "adm4": str(adm4)})

        result = []
        for prov, cities in tree.items():
            prov_obj = {"province": prov, "cities": []}
            for city, dists in cities.items():
                city_obj = {"city": city, "districts": []}
                for dist, info in dists.items():
                    city_obj["districts"].append({
                        "district": dist,
                        "subdistricts": info.get("subdistricts", [])
                    })
                prov_obj["cities"].append(city_obj)
            result.append(prov_obj)

        return jsonify({"provinceList": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # run backend: python "src\Backend\api_service.py"
    app.run(host="0.0.0.0", port=5000, debug=True)