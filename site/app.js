const LAYERS = {
  dental_visit_pct: {
    label: "Dental visit in past year",
    unit: "%",
    higherIsBetter: true,
    description: "Share of adults with a dental visit last year",
  },
  food_insecurity_pct: {
    label: "Food insecurity",
    unit: "%",
    higherIsBetter: false,
    description: "Adults who could not afford enough food",
  },
  clinician_occ_pct: {
    label: "Clinician workforce",
    unit: "%",
    higherIsBetter: true,
    description: "Workers in health diagnosing and treating roles",
  },
  transport_barrier_pct: {
    label: "Transport barriers",
    unit: "%",
    higherIsBetter: false,
    description: "Missed care or daily needs for lack of a ride",
  },
};

const FOCUS_PLACES = {
  8: "South LA, Baldwin Hills, Crenshaw",
  9: "South LA, Watts, Florence",
  10: "West Adams, Koreatown, Mid-City",
};

const RAMP = ["#fff7ed", "#fed7aa", "#fb923c", "#ea580c", "#9a3412"];

let map;
let geoLayer;
let metrics;
let activeLayer = "dental_visit_pct";
let selectedId = 9;

function colorFor(value, values, higherIsBetter) {
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (max === min) return RAMP[2];
  let t = (value - min) / (max - min);
  if (higherIsBetter) t = 1 - t;
  const idx = Math.min(RAMP.length - 1, Math.floor(t * (RAMP.length - 0.0001)));
  return RAMP[idx];
}

function valuesFor(layerKey, features) {
  return features.map((f) => f.properties[layerKey]);
}

function renderLegend(layerKey, features) {
  const cfg = LAYERS[layerKey];
  const vals = valuesFor(layerKey, features);
  const min = Math.min(...vals);
  const max = Math.max(...vals);
  const low = cfg.higherIsBetter ? max : min;
  const high = cfg.higherIsBetter ? min : max;
  const legend = document.getElementById("legend");
  legend.innerHTML = `
    <p class="legend-title">${cfg.label}</p>
    <div class="legend-steps" aria-hidden="true">
      ${RAMP.map((c) => `<span style="background:${c}"></span>`).join("")}
    </div>
    <div class="legend-scale">
      <span>${low.toFixed(0)}${cfg.unit} better</span>
      <span>${high.toFixed(0)}${cfg.unit} worse</span>
    </div>
  `;
}

function renderDistrictCard(props) {
  const card = document.getElementById("district-card");
  const focus = props.focus;
  card.innerHTML = `
    <p class="eyebrow">${focus ? "Focus district" : "Council district"}</p>
    <h2>${props.name}${props.member ? ` · ${props.member}` : ""}</h2>
    <p class="side-copy">${FOCUS_PLACES[props.district] || "Los Angeles City Council district"}</p>
    <ul class="metric-list">
      <li><span>Dental visits</span><strong>${props.dental_visit_pct}%</strong></li>
      <li><span>Food insecurity</span><strong>${props.food_insecurity_pct}%</strong></li>
      <li><span>Clinician workforce</span><strong>${props.clinician_occ_pct}%</strong></li>
      <li><span>Transport barriers</span><strong>${props.transport_barrier_pct}%</strong></li>
      <li><span>Poverty</span><strong>${props.poverty_pct}%</strong></li>
    </ul>
    <div class="legend" id="legend"></div>
  `;
}

function paintLayer(geojson) {
  const features = geojson.features;
  const vals = valuesFor(activeLayer, features);
  const cfg = LAYERS[activeLayer];

  if (geoLayer) map.removeLayer(geoLayer);

  geoLayer = L.geoJSON(geojson, {
    style(feature) {
      return {
        fillColor: colorFor(feature.properties[activeLayer], vals, cfg.higherIsBetter),
        weight: feature.properties.focus ? 2.6 : 1,
        color: feature.properties.focus ? "#1a1a1a" : "#9ca3af",
        fillOpacity: feature.properties.district === selectedId ? 1 : 0.92,
      };
    },
    onEachFeature(feature, layer) {
      layer.bindTooltip(
        `${feature.properties.name}: ${feature.properties[activeLayer]}${cfg.unit}`,
        { className: "district-tip", sticky: true }
      );
      layer.on({
        click() {
          selectedId = feature.properties.district;
          renderDistrictCard(feature.properties);
          renderLegend(activeLayer, features);
          paintLayer(geojson);
        },
        mouseover(e) {
          e.target.setStyle({ weight: 3, color: "#1c1917" });
        },
        mouseout(e) {
          geoLayer.resetStyle(e.target);
        },
      });
    },
  }).addTo(map);

  const selected = features.find((f) => f.properties.district === selectedId);
  if (selected) {
    renderDistrictCard(selected.properties);
    renderLegend(activeLayer, features);
  }

  map.fitBounds(geoLayer.getBounds(), { padding: [18, 18] });
}

function buildBoards(focus) {
  const city = metrics.city;
  const root = document.getElementById("boards");
  root.innerHTML = focus
    .map((d) => {
      const rows = [
        {
          label: "Dental visits",
          value: d.dental_visit_pct,
          max: 75,
          city: city.dental_visit_pct,
          inverse: false,
        },
        {
          label: "Food insecurity",
          value: d.food_insecurity_pct,
          max: 50,
          city: city.food_insecurity_pct,
          inverse: true,
        },
        {
          label: "Clinician workforce",
          value: d.clinician_occ_pct,
          max: 6,
          city: city.clinician_occ_pct,
          inverse: false,
        },
        {
          label: "Transport barriers",
          value: d.transport_barrier_pct,
          max: 25,
          city: city.transport_barrier_pct,
          inverse: true,
        },
      ];
      return `
        <article class="board ${d.district === 9 ? "hot" : ""}">
          <h3>CD ${d.district}</h3>
          <p class="places">${FOCUS_PLACES[d.district]}</p>
          <div class="bars">
            ${rows
              .map((r) => {
                const width = Math.max(4, (r.value / r.max) * 100);
                return `
                <div class="bar-row">
                  <label><span>${r.label}</span><span>${r.value}% · city ${r.city}%</span></label>
                  <div class="track"><div class="fill ${r.inverse ? "inverse" : ""}" style="width:${width}%"></div></div>
                </div>`;
              })
              .join("")}
          </div>
        </article>`;
    })
    .join("");
}

function buildRankChart(districts) {
  const ordered = [...districts].sort((a, b) => a.dental_visit_pct - b.dental_visit_pct);
  const ctx = document.getElementById("rankChart");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: ordered.map((d) => d.name),
      datasets: [
        {
          data: ordered.map((d) => d.dental_visit_pct),
          backgroundColor: ordered.map((d) =>
            d.focus ? "#c2410c" : "#d6d3d1"
          ),
          borderSkipped: false,
          borderRadius: 4,
          barThickness: 14,
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (c) => `${c.parsed.x}% dental visits`,
          },
        },
      },
      scales: {
        x: {
          min: 0,
          max: 80,
          grid: { color: "#f5f5f4" },
          ticks: { callback: (v) => `${v}%`, color: "#78716c" },
          border: { display: false },
        },
        y: {
          grid: { display: false },
          ticks: { color: "#44403c", font: { size: 11 } },
          border: { display: false },
        },
      },
    },
  });
  ctx.parentElement.style.height = "360px";
}

function buildFunnelChart() {
  const ctx = document.getElementById("funnelChart");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: [
        "LA enrolled in Medi-Cal",
        "LA seeing 100+ Medi-Cal patients",
        "CA meaningful adult Medi-Cal",
      ],
      datasets: [
        {
          data: [55, 39, 15],
          backgroundColor: ["#0f766e", "#c2410c", "#b91c1c"],
          borderRadius: 6,
          barThickness: 42,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: (c) => `${c.parsed.y}% of dentists` },
        },
      },
      scales: {
        y: {
          min: 0,
          max: 70,
          ticks: { callback: (v) => `${v}%`, color: "#78716c" },
          grid: { color: "#f5f5f4" },
          border: { display: false },
        },
        x: {
          ticks: { color: "#44403c", font: { size: 11 } },
          grid: { display: false },
          border: { display: false },
        },
      },
    },
  });
  ctx.parentElement.style.height = "260px";
}

async function init() {
  const [geojson, metricsJson] = await Promise.all([
    fetch("data/districts.geojson").then((r) => r.json()),
    fetch("data/metrics.json").then((r) => r.json()),
  ]);
  metrics = metricsJson;

  // Flat choropleth only (no basemap tiles / API keys).
  map = L.map("map", {
    scrollWheelZoom: false,
    zoomControl: true,
    attributionControl: true,
    zoomSnap: 0.25,
  });
  map.attributionControl.setPrefix(false);
  map.attributionControl.addAttribution("LA City Council Districts");

  document.querySelectorAll(".tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      activeLayer = btn.dataset.layer;
      paintLayer(geojson);
    });
  });

  paintLayer(geojson);
  buildBoards(metrics.focus);
  buildRankChart(metrics.districts);
  buildFunnelChart();
}

init();
