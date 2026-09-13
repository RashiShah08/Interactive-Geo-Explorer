/* Renders the generated coastline paths as inline SVG, optionally plotting
   real place coordinates on the same projection. */
const Plot = (() => {
  const SVG_NS = "http://www.w3.org/2000/svg";

  function project(shape, lat, lon) {
    return {
      x: ((lon - shape.lon0) / (shape.lon1 - shape.lon0)) * shape.width,
      y: ((shape.lat1 - lat) / (shape.lat1 - shape.lat0)) * shape.height,
    };
  }

  function el(name, attrs) {
    const node = document.createElementNS(SVG_NS, name);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
    return node;
  }

  function graticule(shape, step) {
    const lines = [];
    for (let lon = shape.lon0; lon <= shape.lon1; lon += step) {
      const { x } = project(shape, 0, lon);
      lines.push(`M${x.toFixed(1)} 0V${shape.height}`);
    }
    for (let lat = shape.lat0; lat <= shape.lat1; lat += step) {
      const { y } = project(shape, lat, 0);
      lines.push(`M0 ${y.toFixed(1)}H${shape.width}`);
    }
    return lines.join("");
  }

  /**
   * @param container  element to render into
   * @param shapeKey   "world" | "india"
   * @param places     optional array of {lat, lon, category, title}
   * @param options    {graticuleStep, colorFor, animate}
   */
  function render(container, shapeKey, places = [], options = {}) {
    const shape = GEO_SHAPES[shapeKey];
    const { graticuleStep = 20, colorFor = () => "#C8553D", animate = true } = options;

    container.innerHTML = "";
    const svg = el("svg", {
      viewBox: shape.viewBox || `0 0 ${shape.width} ${shape.height}`,
      preserveAspectRatio: "xMidYMid meet",
      class: "plot-svg",
    });

    svg.appendChild(el("path", { d: graticule(shape, graticuleStep), class: "plot-grat" }));
    svg.appendChild(el("path", { d: shape.path, class: "plot-land" }));

    const dots = el("g", { class: "plot-dots" });
    places.forEach((place, index) => {
      const { x, y } = project(shape, place.lat, place.lon);
      const dot = el("circle", {
        cx: x.toFixed(1),
        cy: y.toFixed(1),
        r: shapeKey === "world" ? 5 : 6,
        fill: colorFor(place.category),
        class: "plot-dot",
      });
      if (animate) dot.style.animationDelay = `${140 + index * 26}ms`;
      dots.appendChild(dot);
    });
    svg.appendChild(dots);

    if (animate) svg.classList.add("is-animated");
    container.appendChild(svg);
  }

  return { render, project };
})();
