/* The cover plate: the world draws itself, then places land on it in turn.
   A small curated set of coordinates, so the cover paints immediately without
   waiting on a fetch. */
const Hero = (() => {
  const HIGHLIGHTS = [
    { title: "Taj Mahal", lat: 27.1751, lon: 78.0421, color: "#E0785F" },
    { title: "Eiffel Tower", lat: 48.8584, lon: 2.2945, color: "#6AA9D8" },
    { title: "Machu Picchu", lat: -13.1631, lon: -72.545, color: "#7FB08A" },
    { title: "Pyramids of Giza", lat: 29.9792, lon: 31.1342, color: "#D9A441" },
    { title: "Great Wall of China", lat: 40.4319, lon: 116.5704, color: "#E0785F" },
    { title: "Statue of Liberty", lat: 40.6892, lon: -74.0445, color: "#9B8BC4" },
    { title: "Sydney Opera House", lat: -33.8568, lon: 151.2153, color: "#C77FA6" },
    { title: "Victoria Falls", lat: -17.9243, lon: 25.8572, color: "#D9A441" },
  ];

  const SVG_NS = "http://www.w3.org/2000/svg";
  const DRAW_MS = 2200;
  const DOT_GAP = 190;
  const TICK_MS = 2600;

  let timers = [];
  let started = false;

  const reduced = () =>
    window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;

  const after = (fn, ms) => { timers.push(setTimeout(fn, ms)); };

  function formatCoord({ lat, lon }) {
    return (
      `${Math.abs(lat).toFixed(4)}° ${lat >= 0 ? "N" : "S"}, ` +
      `${Math.abs(lon).toFixed(4)}° ${lon >= 0 ? "E" : "W"}`
    );
  }

  function countUp(el, target, duration = 900) {
    if (reduced()) { el.textContent = target; return; }
    const start = performance.now();
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = Math.round(target * eased);
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  function drawCoastline(svg) {
    const land = svg.querySelector(".plot-land");
    if (!land) return 0;

    if (reduced()) { land.classList.add("is-drawn"); return 0; }

    const length = land.getTotalLength();
    land.style.strokeDasharray = `${length}`;
    land.style.strokeDashoffset = `${length}`;
    land.style.transition = `stroke-dashoffset ${DRAW_MS}ms cubic-bezier(0.22,0.61,0.36,1)`;
    // Next frame, so the starting offset is committed before the transition.
    requestAnimationFrame(() => requestAnimationFrame(() => {
      land.style.strokeDashoffset = "0";
    }));
    after(() => land.classList.add("is-drawn"), DRAW_MS * 0.72);
    return DRAW_MS * 0.62;
  }

  function plotHighlights(svg, shape, startAt) {
    const layer = document.createElementNS(SVG_NS, "g");
    layer.setAttribute("class", "hero-dots");
    svg.appendChild(layer);

    const nodes = HIGHLIGHTS.map((place) => {
      const { x, y } = Plot.project(shape, place.lat, place.lon);
      const group = document.createElementNS(SVG_NS, "g");
      group.setAttribute("class", "hero-dot");

      const ring = document.createElementNS(SVG_NS, "circle");
      ring.setAttribute("cx", x.toFixed(1));
      ring.setAttribute("cy", y.toFixed(1));
      ring.setAttribute("r", "6.5");
      ring.setAttribute("class", "hero-ring");
      ring.setAttribute("stroke", place.color);

      const dot = document.createElementNS(SVG_NS, "circle");
      dot.setAttribute("cx", x.toFixed(1));
      dot.setAttribute("cy", y.toFixed(1));
      dot.setAttribute("r", "6.5");
      dot.setAttribute("fill", place.color);
      dot.setAttribute("class", "hero-core");

      group.append(ring, dot);
      layer.appendChild(group);
      return group;
    });

    if (reduced()) {
      nodes.forEach((node) => node.classList.add("is-on"));
      return;
    }

    nodes.forEach((node, i) => after(() => node.classList.add("is-on"), startAt + i * DOT_GAP));
    return startAt + nodes.length * DOT_GAP;
  }

  function runTicker(svg, firstAt) {
    const nameEl = document.getElementById("ticker-name");
    const coordEl = document.getElementById("ticker-coord");
    const dots = svg.querySelectorAll(".hero-dot");
    if (!nameEl || !coordEl) return;

    let i = 0;
    const show = (index) => {
      const place = HIGHLIGHTS[index];
      nameEl.textContent = place.title;
      coordEl.textContent = formatCoord(place);
      nameEl.parentElement.classList.remove("is-swap");
      void nameEl.parentElement.offsetWidth;
      nameEl.parentElement.classList.add("is-swap");
      dots.forEach((dot, d) => dot.classList.toggle("is-lit", d === index));
    };

    after(() => {
      show(0);
      if (reduced()) return;
      timers.push(setInterval(() => {
        i = (i + 1) % HIGHLIGHTS.length;
        show(i);
      }, TICK_MS));
    }, firstAt);
  }

  function parallax(container) {
    if (reduced()) return;
    const plate = container.closest(".auth-plate");
    if (!plate) return;

    let raf = null;
    plate.addEventListener("mousemove", (event) => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        const box = plate.getBoundingClientRect();
        const dx = (event.clientX - box.left) / box.width - 0.5;
        const dy = (event.clientY - box.top) / box.height - 0.5;
        container.style.transform = `translate(${(-dx * 14).toFixed(1)}px, ${(-dy * 10).toFixed(1)}px)`;
        raf = null;
      });
    });
    plate.addEventListener("mouseleave", () => { container.style.transform = ""; });
  }

  function start() {
    if (started) return;
    started = true;

    const container = document.getElementById("auth-map");
    Plot.render(container, "world", [], { animate: false });

    const svg = container.querySelector("svg");
    const shape = GEO_SHAPES.world;
    svg.classList.add("is-hero");

    const dotsAt = drawCoastline(svg);
    const doneAt = plotHighlights(svg, shape, dotsAt) ?? 0;
    runTicker(svg, reduced() ? 0 : dotsAt + 120);
    parallax(container);

    document.querySelectorAll(".figures dd[data-count]").forEach((el, i) => {
      after(() => countUp(el, Number(el.dataset.count)), 420 + i * 130);
    });

    return doneAt;
  }

  function stop() {
    timers.forEach((t) => { clearTimeout(t); clearInterval(t); });
    timers = [];
    started = false;
  }

  return { start, stop };
})();
