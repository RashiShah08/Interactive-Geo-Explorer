(() => {
  const VIEWS = ["auth", "home", "map"];
  let routing = false;
  let currentUser = null;
  let pendingAction = null;   // what the visitor was trying to do when asked to sign in
  let returnHash = "";        // where they were, so sign-in doesn't lose their place

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

    const browsing = name !== "auth";
    if (!browsing) Chat.close();
    // Must follow Chat.close(): closing the panel restores the launcher button.
    document.getElementById("chat-fab").classList.toggle("is-hidden", !browsing);
    if (name === "auth") { AuthHero.stop(); AuthHero.start(); Auth.focus(); }
  }

  function renderAuthControls() {
    const signedIn = Boolean(currentUser);
    const chip = document.getElementById("home-user");
    chip.textContent = currentUser || "";
    chip.classList.toggle("is-hidden", !signedIn);
    document.getElementById("logout-btn").classList.toggle("is-hidden", !signedIn);
    document.getElementById("signin-btn").classList.toggle("is-hidden", signedIn);
  }

  /** Run `action` if signed in; otherwise send them to sign-in and run it afterwards. */
  function requireAuth(action, reason) {
    if (currentUser) { action(); return; }

    pendingAction = action;
    returnHash = window.location.hash;

    const note = document.getElementById("auth-reason");
    note.textContent = reason;
    note.classList.remove("is-hidden");
    showView("auth");
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

  function goHome() {
    showView("home");
    setHash("");
  }

  let everywhere = [];

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

  function randomPlace() {
    if (!everywhere.length) return;
    const pick = everywhere[Math.floor(Math.random() * everywhere.length)];
    openAtlas(pick.atlas, pick.place.key);
  }

  function renderAtlasPlots(world, india) {
    const options = { colorFor: (category) => GeoMap.colorFor(category) };
    Plot.render(document.querySelector('[data-plot="world"]'), "world", world, options);
    Plot.render(document.querySelector('[data-plot="india"]'), "india", india, {
      ...options,
      graticuleStep: 10,
    });
  }

  async function applyHash() {
    const match = window.location.hash.match(/^#\/(world|india)(?:\/([a-z_]+))?$/);
    if (!match) { showView("home"); return; }
    await openAtlas(match[1], match[2] || null);
  }

  /** Called after a successful sign-in: go back where they were, finish what they started. */
  async function afterSignIn(username) {
    currentUser = username;
    renderAuthControls();
    document.getElementById("auth-reason").classList.add("is-hidden");
    AuthHero.stop();

    if (returnHash) {
      window.location.hash = returnHash;
      returnHash = "";
      await applyHash();
    } else {
      showView("home");
    }

    const action = pendingAction;
    pendingAction = null;
    if (action) setTimeout(action, 260);
  }

  async function boot() {
    Auth.init(afterSignIn);
    Chat.init({
      onCitation: (atlas, placeKey) => openAtlas(atlas, placeKey),
    });
    GeoMap.init({
      ask: (place) => Chat.askAbout(place),
      select: (atlas, placeKey) => setHash(placeKey ? `#/${atlas}/${placeKey}` : `#/${atlas}`),
    });
    Palette.init((atlas, placeKey) => openAtlas(atlas, placeKey));

    document.querySelectorAll(".atlas-card").forEach((card) => {
      const go = () => openAtlas(card.dataset.atlas);
      card.addEventListener("click", go);
      card.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") { event.preventDefault(); go(); }
      });
    });

    document.getElementById("back-btn").addEventListener("click", goHome);
    document.getElementById("home-random").addEventListener("click", randomPlace);
    document.getElementById("home-search").addEventListener("click", () => Palette.open());
    document.getElementById("map-search").addEventListener("click", () => Palette.open());
    document.getElementById("auth-skip").addEventListener("click", async () => {
      pendingAction = null;
      AuthHero.stop();
      if (returnHash) {
        window.location.hash = returnHash;
        returnHash = "";
        await applyHash();
      } else {
        showView("home");
      }
    });
    document.getElementById("signin-btn").addEventListener("click", () => {
      returnHash = window.location.hash;
      document.getElementById("auth-reason").classList.add("is-hidden");
      showView("auth");
    });
    document.getElementById("logout-btn").addEventListener("click", async () => {
      await API.logout();
      currentUser = null;
      Chat.reset();
      renderAuthControls();
      toast("Signed out — you can keep browsing.");
    });

    window.addEventListener("hashchange", () => {
      if (routing) return;
      if (document.getElementById("view-auth").classList.contains("is-hidden")) applyHash();
    });

    // Browsing is public: load straight into the atlas, signed in or not.
    buildSearchIndex();

    const { ok, body } = await API.me();
    currentUser = ok && body?.username ? body.username : null;
    renderAuthControls();

    if (window.location.hash) await applyHash();
    else showView("home");
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
