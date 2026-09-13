(() => {
  const VIEWS = ["landing", "home", "map"];
  let routing = false;
  let everywhere = [];

  function toast(text) {
    const node = document.getElementById("toast");
    node.textContent = text;
    node.classList.add("is-on");
    clearTimeout(node._timer);
    node._timer = setTimeout(() => node.classList.remove("is-on"), 2600);
  }

  function showView(name) {
    VIEWS.forEach((view) => {
      document.getElementById(`view-${view}`).classList.toggle("is-hidden", view !== name);
    });
    document.body.classList.toggle("is-map-view", name === "map");

    const inApp = name !== "landing";
    if (!inApp) Chat.close();
    // Must follow Chat.close(): closing the panel restores the launcher button.
    document.getElementById("chat-fab").classList.toggle("is-hidden", !inApp);

    if (name === "landing") { Hero.stop(); Hero.start(); }
  }

  function setHash(value) {
    routing = true;
    if (value) window.location.hash = value;
    else history.replaceState(null, "", window.location.pathname);
    setTimeout(() => { routing = false; }, 0);
  }

  async function openAtlas(key, placeKey = null) {
    showView("map");
    try {
      await GeoMap.open(key, placeKey);
      setHash(placeKey ? `#/${key}/${placeKey}` : `#/${key}`);
    } catch {
      toast("Could not load that atlas.");
      showView("home");
    }
  }

  async function buildSearchIndex() {
    try {
      const [world, india] = await Promise.all([GeoMap.load("world"), GeoMap.load("india")]);
      everywhere = [
        ...world.map((place) => ({ atlas: "world", place, color: GeoMap.colorFor(place.category) })),
        ...india.map((place) => ({ atlas: "india", place, color: GeoMap.colorFor(place.category) })),
      ];
      Palette.setIndex(everywhere);
      renderAtlasPlots(world, india);
    } catch {
      /* Search and card plots are enhancements; the app works without them. */
    }
  }

  function renderAtlasPlots(world, india) {
    const options = { colorFor: (category) => GeoMap.colorFor(category) };
    Plot.render(document.querySelector('[data-plot="world"]'), "world", world, options);
    Plot.render(document.querySelector('[data-plot="india"]'), "india", india, {
      ...options,
      graticuleStep: 10,
    });
  }

  function randomPlace() {
    if (!everywhere.length) return;
    const pick = everywhere[Math.floor(Math.random() * everywhere.length)];
    openAtlas(pick.atlas, pick.place.key);
  }

  async function applyHash() {
    const match = window.location.hash.match(/^#\/(world|india)(?:\/([a-z_]+))?$/);
    if (!match) return false;
    await openAtlas(match[1], match[2] || null);
    return true;
  }

  function boot() {
    Chat.init({ onCitation: (atlas, placeKey) => openAtlas(atlas, placeKey) });
    GeoMap.init({
      ask: (place) => Chat.askAbout(place),
      select: (atlas, placeKey) => setHash(placeKey ? `#/${atlas}/${placeKey}` : `#/${atlas}`),
    });
    Palette.init((atlas, placeKey) => openAtlas(atlas, placeKey));

    document.querySelectorAll("[data-atlas]").forEach((node) => {
      const go = () => openAtlas(node.dataset.atlas);
      node.addEventListener("click", go);
      node.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") { event.preventDefault(); go(); }
      });
    });

    document.getElementById("back-btn").addEventListener("click", () => {
      showView("home");
      setHash("");
    });
    document.getElementById("home-cover").addEventListener("click", () => {
      showView("landing");
      setHash("");
    });
    document.getElementById("home-random").addEventListener("click", randomPlace);
    document.getElementById("enter-search").addEventListener("click", () => Palette.open());
    document.getElementById("home-search").addEventListener("click", () => Palette.open());
    document.getElementById("map-search").addEventListener("click", () => Palette.open());

    window.addEventListener("hashchange", () => {
      if (!routing) applyHash();
    });

    buildSearchIndex();

    // A shared link goes straight to the place; everyone else gets the cover.
    if (window.location.hash) applyHash().then((ok) => { if (!ok) showView("landing"); });
    else showView("landing");
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
