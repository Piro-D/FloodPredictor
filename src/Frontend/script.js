const provinceSelect = document.getElementById("province");
const citySelect = document.getElementById("city");
const districtSelect = document.getElementById("district");
const subdistrictSelect = document.getElementById("subdistrict");
const resultsDiv = document.getElementById("results");

document.getElementById("checkFlood").addEventListener("click", async () => {
    const province = provinceSelect.options[provinceSelect.selectedIndex]?.text.trim() || provinceSelect.value;
    const city = citySelect.options[citySelect.selectedIndex]?.text.trim() || citySelect.value;
    const district = districtSelect.options[districtSelect.selectedIndex]?.text.trim() || districtSelect.value;
    const subdistrict = subdistrictSelect.options[subdistrictSelect.selectedIndex]?.text.trim() || subdistrictSelect.value;

    if (!province || !city || !district || !subdistrict) {
        resultsDiv.textContent = "Please select all fields!";
        return;
    }

    resultsDiv.textContent = "Requesting backend prediction...";
    const forceHeavy = document.getElementById("forceHeavyRain")?.checked;

    try {
        const resp = await fetch("http://localhost:5000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                kelurahan: subdistrict,
                province,
                city,
                district,
                force_rain_level: forceHeavy ? 3 : undefined
            })
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

        let html = `
            <h3 style="margin-bottom:12px;">Predictions for ${subdistrict}</h3>
            <div class="prediction-grid">
        `;

        rows.forEach(r => {
            let statusClass, badgeClass, badgeText;

            if (r.flood_prediction === 1) {
                statusClass = "danger";
                badgeClass = "badge-danger";
                badgeText = "BANJIR";
            } else if (Number(r.probability) >= 30) {
                statusClass = "warning";
                badgeClass = "badge-warning";
                badgeText = "WASPADA";
            } else {
                statusClass = "safe";
                badgeClass = "badge-safe";
                badgeText = "AMAN";
            }

            html += `
                <div class="prediction-card ${statusClass}">
                    <div class="prediction-header">
                        <div class="prediction-date">${r.datetime}</div>
                        <div class="prediction-badge ${badgeClass}">${badgeText}</div>
                    </div>
                    <div class="prediction-body">
                        Weather: <span>${r.weather ?? "-"}</span><br>
                        Temperature: <span>${r.temperature ?? "-"} °C</span><br>
                        Humidity: <span>${r.humidity ?? "-"}%</span><br>
                        Flood Probability: <span>${r.probability !== null ? Number(r.probability).toFixed(1) + "%" : "-"}</span>
                    </div>
                </div>
            `;
        });

        html += `</div>`;
        resultsDiv.innerHTML = html;

    } catch (err) {
        console.error(err);
        resultsDiv.textContent = "Error getting prediction. Open DevTools Console for details.";
    }
});



async function loadAreas() {
    resultsDiv.textContent = "Loading area list...";
    try {
        const resp = await fetch("http://localhost:5000/areas");
        if (!resp.ok) throw new Error("Failed to load areas");

        const json = await resp.json();
        const provinceList = json.provinceList || [];

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

        window.__AREA_TREE = provinceList;
        resultsDiv.textContent = "";

    } catch (err) {
        console.error(err);
        resultsDiv.textContent = "Failed to load areas.";
    }
}

function getCitiesForProvince(province) {
    const tree = window.__AREA_TREE || [];
    return (tree.find(p => p.province === province) || {}).cities || [];
}

function getDistrictsForProvinceCity(province, city) {
    const cities = getCitiesForProvince(province);
    return (cities.find(c => c.city === city) || {}).districts || [];
}

provinceSelect.addEventListener("change", () => {
    citySelect.innerHTML = '<option value="">Select City</option>';
    districtSelect.innerHTML = '<option value="">Select District</option>';
    subdistrictSelect.innerHTML = '<option value="">Select Subdistrict</option>';
    districtSelect.disabled = true;
    subdistrictSelect.disabled = true;

    getCitiesForProvince(provinceSelect.value).forEach(c => {
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

    getDistrictsForProvinceCity(provinceSelect.value, citySelect.value).forEach(d => {
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

    if (!d) return;

    d.subdistricts.forEach(s => {
        const opt = document.createElement("option");
        opt.value = s.name;
        opt.textContent = s.name;
        subdistrictSelect.appendChild(opt);
    });
    subdistrictSelect.disabled = false;
});

loadAreas();
