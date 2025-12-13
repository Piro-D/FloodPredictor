const provinceSelect = document.getElementById("province");
const citySelect = document.getElementById("city");
const districtSelect = document.getElementById("district");
const subdistrictSelect = document.getElementById("subdistrict");
const resultsDiv = document.getElementById("results");

// ...existing code...
document.getElementById("checkFlood").addEventListener("click", async () => {
    // use option text (displayed/canonical name) instead of option value (which was ADM code)
    const province = provinceSelect.options[provinceSelect.selectedIndex]?.text.trim() || provinceSelect.value;
    const city = citySelect.options[citySelect.selectedIndex]?.text.trim() || citySelect.value;
    const district = districtSelect.options[districtSelect.selectedIndex]?.text.trim() || districtSelect.value;
    const subdistrict = subdistrictSelect.options[subdistrictSelect.selectedIndex]?.text.trim() || subdistrictSelect.value; // canonical kelurahan

    if (!province || !city || !district || !subdistrict) {
        resultsDiv.textContent = "Please select all fields!";
        return;
    }

    resultsDiv.textContent = "Requesting backend prediction...";

    try {
        const resp = await fetch("http://localhost:5000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ kelurahan: subdistrict, province, city, district })
        });

        if (!resp.ok) {
            const txt = await resp.text().catch(() => "");
            throw new Error(`Server ${resp.status}: ${txt}`);
        }

        const json = await resp.json();
        if (json.error) {
            resultsDiv.textContent = `Backend error: ${json.error}`;
            return;
        }

        const rows = json.results || [];
        if (rows.length === 0) {
            resultsDiv.innerHTML = `<strong>No results for ${subdistrict}</strong>`;
            return;
        }

        let html = `<h3>Predictions for ${subdistrict}</h3><div class="pred-list">`;
        rows.forEach((r, i) => {
            html += `
                <div class="pred-item">
                    <strong>Forecast ${i+1}</strong>
                    <div>Date/Time: ${r.datetime}</div>
                    <div>Weather: ${r.weather ?? "-"}</div>
                    <div>Temperature: ${r.temperature ?? "-"} °C</div>
                    <div>Humidity: ${r.humidity ?? "-"}%</div>
                    <div>Flood Predicted: ${r.flood_prediction === 1 ? "YES" : "NO"}</div>
                    <div>Flood Prob: ${r.probability !== null ? (Number(r.probability).toFixed(1) + "%") : "-"}</div>
                </div><hr/>`;
        });
        html += `</div>`;
        resultsDiv.innerHTML = html;
    } catch (err) {
        console.error(err);
        resultsDiv.textContent = "Error getting prediction. Open DevTools Console for details.";
    }
});
// remove or replace the hardcoded `data` and population logic with runtime fetch

async function loadAreas() {
    resultsDiv.textContent = "Loading area list...";
    try {
        const resp = await fetch("http://localhost:5000/areas");
        if (!resp.ok) {
            const txt = await resp.text().catch(() => "");
            throw new Error(`Server ${resp.status}: ${txt}`);
        }
        const json = await resp.json();
        const provinceList = json.provinceList || [];

        // clear selects
        provinceSelect.innerHTML = '<option value="">Select Province</option>';
        citySelect.innerHTML = '<option value="">Select City</option>';
        districtSelect.innerHTML = '<option value="">Select District</option>';
        subdistrictSelect.innerHTML = '<option value="">Select Subdistrict</option>';
        citySelect.disabled = true;
        districtSelect.disabled = true;
        subdistrictSelect.disabled = true;

        provinceList.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p.province;
            opt.textContent = p.province;
            provinceSelect.appendChild(opt);
        });

        // store the structure for client-side use
        window.__AREA_TREE = provinceList;
        resultsDiv.textContent = "";
    } catch (err) {
        console.error(err);
        resultsDiv.textContent = "Failed to load areas. Make sure backend is running and /areas is available.";
    }
}

// helper to get data arrays from loaded tree
function getCitiesForProvince(province) {
    const tree = window.__AREA_TREE || [];
    const p = tree.find(x => x.province === province);
    return p ? p.cities : [];
}
function getDistrictsForProvinceCity(province, city) {
    const cities = getCitiesForProvince(province);
    const c = cities.find(x => x.city === city);
    return c ? c.districts : [];
}

// wire selects (replace previous event listeners)
provinceSelect.addEventListener("change", () => {
    citySelect.innerHTML = '<option value="">Select City</option>';
    districtSelect.innerHTML = '<option value="">Select District</option>';
    subdistrictSelect.innerHTML = '<option value="">Select Subdistrict</option>';
    districtSelect.disabled = true;
    subdistrictSelect.disabled = true;

    const cities = getCitiesForProvince(provinceSelect.value);
    if (!cities || cities.length === 0) {
        citySelect.disabled = true;
        return;
    }
    cities.forEach(c => {
        const opt = document.createElement("option");
        opt.value = c.city;
        opt.textContent = c.city;
        citySelect.appendChild(opt);
    });
    citySelect.disabled = false;
});

citySelect.addEventListener("change", () => {
    districtSelect.innerHTML = '<option value="">Select District</option>';
    subdistrictSelect.innerHTML = '<option value="">Select Subdistrict</option>';
    subdistrictSelect.disabled = true;

    const districts = getDistrictsForProvinceCity(provinceSelect.value, citySelect.value);
    if (!districts || districts.length === 0) {
        districtSelect.disabled = true;
        return;
    }
    districts.forEach(d => {
        const opt = document.createElement("option");
        opt.value = d.district;
        opt.textContent = d.district;
        districtSelect.appendChild(opt);
    });
    districtSelect.disabled = false;
});

districtSelect.addEventListener("change", () => {
    subdistrictSelect.innerHTML = '<option value="">Select Subdistrict</option>';
    const districts = getDistrictsForProvinceCity(provinceSelect.value, citySelect.value);
    const d = districts.find(x => x.district === districtSelect.value);
    if (!d || !d.subdistricts) {
        subdistrictSelect.disabled = true;
        return;
    }
    d.subdistricts.forEach(s => {
        const opt = document.createElement("option");
        // keep option.value as canonical name (use name) and you can also attach adm4 if needed
        opt.value = s.name;
        opt.textContent = s.name;
        opt.dataset.adm4 = s.adm4 || "";
        subdistrictSelect.appendChild(opt);
    });
    subdistrictSelect.disabled = false;
});

// call loader at startup
loadAreas();

