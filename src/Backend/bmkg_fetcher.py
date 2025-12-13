import requests
from requests.exceptions import RequestException

def fetch_bmkg_forecast(adm4_code: str):
    url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={adm4_code}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    except RequestException as e:
        print(f"[WARN] BMKG fetch failed for adm4={adm4_code}: {e}")
        return None
