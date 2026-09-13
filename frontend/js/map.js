const GeoMap = (() => {
  const CATEGORY_COLORS = {
    Asia: "#E0785F",
    Europe: "#6AA9D8",
    Africa: "#D9A441",
    "North America": "#9B8BC4",
    "South America": "#7FB08A",
    Australia: "#C77FA6",
    "North India": "#6AA9D8",
    "South India": "#7FB08A",
    "East India": "#D9A441",
    "West India": "#E0785F",
    "Central India": "#C77FA6",
    "Northeast India": "#9B8BC4",
  };

  const ATLASES = {
    world: { title: "The World", center: [22, 12], zoom: 2, fetch: () => API.worldPlaces() },
    india: { title: "India", center: [22.4, 80], zoom: 5, fetch: () => API.indiaPlaces() },
  };

  const cache = {};
  let map = null;
  let markers = new Map();
  let places = [];
  let atlasKey = null;
  let activeCategories = new Set();
  let selectedKey = null;
  let onAsk = () => {};
  let onSelect = () => {};

  const colorFor = (category) => CATEGORY_COLORS[category] || "#C8553D";
  const visiblePlaces = () => places.filter((p) => activeCategories.has(p.category));

  function ensureMap() {
    if (map) return map;

    // Top-left keeps the zoom buttons clear of the chat launcher and the
    // coordinate readout, which both sit along the bottom edge.
    map = L.map("leaflet-map", { zoomControl: false, worldCopyJump: true, minZoom: 2 });
    L.control.zoom({ position: "topleft" }).addTo(map);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(map);

    const readout = document.getElementById("coord-readout");
    map.on("mousemove", (event) => {
      readout.textContent = `${event.latlng.lat.toFixed(3)}°, ${event.latlng.lng.toFixed(3)}°`;
      readout.classList.add("is-live");
    });
    map.on("mouseout", () => readout.classList.remove("is-live"));
    map.on("click", (event) => {
      if (!event.originalEvent.target.closest(".pin")) clearSelection();
    });

    return map;
  }

  function makeIcon(place, isActive) {
    return L.divIcon({
      className: "",
      iconSize: [28, 28],
      iconAnchor: [14, 14],
      html:
        `<span class="pin${isActive ? " is-active" : ""}" style="--pin:${colorFor(place.category)}">` +
        `<span class="pin-dot"></span></span>`,
    });
  }

  function renderMarkers() {
    markers.forEach(({ marker }) => marker.remove());
    markers = new Map();

    visiblePlaces().forEach((place, i) => {
      const marker = L.marker([place.lat, place.lon], {
        icon: makeIcon(place, place.key === selectedKey),
        riseOnHover: true,
        keyboard: false,
      })
        .bindTooltip(place.title, { className: "pin-tip", direction: "top", offset: [0, -13] })
        .on("click", () => select(place.key))
        .addTo(map);

      // Stagger the entrance so the data visibly lands rather than blinking in.
      const pin = marker.getElement()?.querySelector(".pin");
      if (pin) pin.style.animationDelay = `${Math.min(i * 22, 620)}ms`;

      markers.set(place.key, { marker, place });
    });

    document.getElementById("map-count").textContent =
      `${visiblePlaces().length} / ${places.length} plotted`;
  }

  function refreshIcons() {
    markers.forEach(({ marker, place }) => {
      marker.setIcon(makeIcon(place, place.key === selectedKey));
    });
  }

  function select(key, { fly = true } = {}) {
    const place = places.find((item) => item.key === key);
    if (!place) return;

    // Selecting something hidden by a filter would leave it invisible.
    if (!activeCategories.has(place.category)) {
      activeCategories.add(place.category);
      syncFilterPills();
      renderMarkers();
    }

    selectedKey = key;
    refreshIcons();

    if (fly) {
      const zoom = Math.max(map.getZoom(), atlasKey === "india" ? 6 : 4);
      map.flyTo([place.lat, place.lon], zoom, { duration: 0.7 });
    }

    const list = visiblePlaces();
    const position = list.findIndex((item) => item.key === key);

    document.getElementById("detail-empty").classList.add("is-hidden");

    const content = document.getElementById("detail-content");
    content.classList.remove("is-hidden", "is-entering");
    void content.offsetWidth;
    content.classList.add("is-entering");

    const image = document.getElementById("detail-image");
    image.src = place.image_url;
    image.alt = place.title;

    document.getElementById("detail-index").textContent =
      `${String(position + 1).padStart(2, "0")} / ${String(list.length).padStart(2, "0")}`;
    document.getElementById("detail-category").textContent = place.category;
    document.getElementById("detail-title").textContent = place.title;
    document.getElementById("detail-coords").textContent =
      `${Math.abs(place.lat).toFixed(4)}° ${place.lat >= 0 ? "N" : "S"}, ` +
      `${Math.abs(place.lon).toFixed(4)}° ${place.lon >= 0 ? "E" : "W"}`;
    document.getElementById("detail-description").textContent = place.description;
    document.getElementById("detail-ask").onclick = () => onAsk(place);

    onSelect(atlasKey, key);
  }

  function step(delta) {
    const list = visiblePlaces();
    if (!list.length) return;
    const current = list.findIndex((item) => item.key === selectedKey);
    const next = current === -1 ? 0 : (current + delta + list.length) % list.length;
    select(list[next].key);
  }

  function shuffle() {
    const list = visiblePlaces().filter((item) => item.key !== selectedKey);
    if (!list.length) return;
    select(list[Math.floor(Math.random() * list.length)].key);
  }

  function recentre() {
    const place = places.find((item) => item.key === selectedKey);
    if (place) map.flyTo([place.lat, place.lon], Math.max(map.getZoom(), 6), { duration: 0.6 });
  }

  function clearSelection() {
    selectedKey = null;
    refreshIcons();
    document.getElementById("detail-empty").classList.remove("is-hidden");
    document.getElementById("detail-content").classList.add("is-hidden");
    onSelect(atlasKey, null);
  }

  function syncFilterPills() {
    document.querySelectorAll("#filter-bar .pill").forEach((pill) => {
      pill.classList.toggle("is-on", activeCategories.has(pill.dataset.category));
    });
  }

  function renderFilters() {
    const categories = [...new Set(places.map((place) => place.category))].sort();
    const bar = document.getElementById("filter-bar");
    bar.innerHTML = "";

    categories.forEach((category) => {
      const pill = document.createElement("button");
      pill.type = "button";
      pill.className = "pill is-on";
      pill.dataset.category = category;
      pill.style.setProperty("--pin", colorFor(category));
      pill.innerHTML = `<span class="pill-swatch"></span>`;
      pill.appendChild(document.createTextNode(category));
      pill.addEventListener("click", () => {
        if (activeCategories.has(category)) activeCategories.delete(category);
        else activeCategories.add(category);
        pill.classList.toggle("is-on", activeCategories.has(category));

        const selected = places.find((item) => item.key === selectedKey);
        if (selected && !activeCategories.has(selected.category)) clearSelection();
        renderMarkers();
      });
      bar.appendChild(pill);
    });
  }

  async function load(key) {
    if (cache[key]) return cache[key];
    const { ok, body } = await ATLASES[key].fetch();
    if (!ok) throw new Error("Could not load places");
    cache[key] = body;
    return body;
  }

  async function open(key, placeKey = null) {
    const atlas = ATLASES[key];
    atlasKey = key;
    document.getElementById("map-title").textContent = atlas.title;

    const loading = document.getElementById("map-loading");
    loading.classList.remove("is-hidden");

    try {
      places = await load(key);
    } finally {
      loading.classList.add("is-hidden");
    }

    activeCategories = new Set(places.map((place) => place.category));
    selectedKey = null;
    document.getElementById("detail-empty").classList.remove("is-hidden");
    document.getElementById("detail-content").classList.add("is-hidden");

    ensureMap();
    map.setView(atlas.center, atlas.zoom);
    renderFilters();
    renderMarkers();
    setTimeout(() => map.invalidateSize(), 60);

    if (placeKey) setTimeout(() => select(placeKey), 120);
  }

  function init({ ask, select: selectCallback }) {
    onAsk = ask;
    onSelect = selectCallback;

    document.getElementById("detail-prev").addEventListener("click", () => step(-1));
    document.getElementById("detail-next").addEventListener("click", () => step(1));
    document.getElementById("detail-coords").addEventListener("click", recentre);
    document.getElementById("map-shuffle").addEventListener("click", shuffle);

    document.addEventListener("keydown", (event) => {
      const typing = ["INPUT", "TEXTAREA"].includes(event.target.tagName);
      const onMap = !document.getElementById("view-map").classList.contains("is-hidden");
      if (typing || !onMap || Palette.isOpen()) return;

      if (event.key === "ArrowRight") { event.preventDefault(); step(1); }
      else if (event.key === "ArrowLeft") { event.preventDefault(); step(-1); }
      else if (event.key === "Escape" && selectedKey) { event.preventDefault(); clearSelection(); }
    });
  }

  return { init, open, select, load, colorFor, CATEGORY_COLORS };
})();
