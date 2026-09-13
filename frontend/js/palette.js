const Palette = (() => {
  let index = [];          // [{ atlas, place }]
  let results = [];
  let cursor = 0;
  let onPick = () => {};

  const root = () => document.getElementById("palette");
  const input = () => document.getElementById("palette-input");
  const list = () => document.getElementById("palette-results");

  const isOpen = () => root().classList.contains("is-open");

  function score(entry, query) {
    const title = entry.place.title.toLowerCase();
    const category = entry.place.category.toLowerCase();
    if (!query) return 1;
    if (title.startsWith(query)) return 100;
    if (title.includes(query)) return 60;
    if (category.includes(query)) return 30;
    if (entry.place.description.toLowerCase().includes(query)) return 10;
    return 0;
  }

  function render() {
    const node = list();
    node.innerHTML = "";

    if (!results.length) {
      const empty = document.createElement("li");
      empty.className = "palette-empty";
      empty.textContent = "Nothing matches that.";
      node.appendChild(empty);
      return;
    }

    results.forEach((entry, i) => {
      const item = document.createElement("li");
      item.className = `palette-item${i === cursor ? " is-cursor" : ""}`;
      item.innerHTML =
        `<span class="palette-dot" style="background:${entry.color}"></span>` +
        `<span class="palette-name"></span>` +
        `<span class="palette-cat"></span>`;
      item.querySelector(".palette-name").textContent = entry.place.title;
      item.querySelector(".palette-cat").textContent = entry.place.category;
      item.addEventListener("click", () => pick(i));
      item.addEventListener("mousemove", () => {
        if (cursor === i) return;
        cursor = i;
        render();
      });
      node.appendChild(item);
    });

    node.querySelector(".is-cursor")?.scrollIntoView({ block: "nearest" });
  }

  function search(query) {
    const q = query.trim().toLowerCase();
    results = index
      .map((entry) => ({ entry, s: score(entry, q) }))
      .filter((row) => row.s > 0)
      .sort((a, b) => b.s - a.s || a.entry.place.title.localeCompare(b.entry.place.title))
      .slice(0, 40)
      .map((row) => row.entry);
    cursor = 0;
    render();
  }

  function pick(i) {
    const entry = results[i];
    if (!entry) return;
    close();
    onPick(entry.atlas, entry.place.key);
  }

  function open() {
    if (!index.length) return;
    root().classList.add("is-open");
    root().setAttribute("aria-hidden", "false");
    input().value = "";
    search("");
    input().focus();
  }

  function close() {
    root().classList.remove("is-open");
    root().setAttribute("aria-hidden", "true");
  }

  function setIndex(entries) {
    index = entries;
  }

  function init(pickCallback) {
    onPick = pickCallback;

    input().addEventListener("input", (event) => search(event.target.value));

    document.addEventListener("keydown", (event) => {
      const key = event.key.toLowerCase();

      if ((event.ctrlKey || event.metaKey) && key === "k") {
        event.preventDefault();
        isOpen() ? close() : open();
        return;
      }

      if (!isOpen()) return;

      if (event.key === "Escape") { event.preventDefault(); close(); }
      else if (event.key === "ArrowDown") {
        event.preventDefault();
        cursor = Math.min(cursor + 1, results.length - 1);
        render();
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        cursor = Math.max(cursor - 1, 0);
        render();
      } else if (event.key === "Enter") {
        event.preventDefault();
        pick(cursor);
      }
    });

    root().querySelector('[data-close="palette"]').addEventListener("click", close);
  }

  return { init, setIndex, open, close, isOpen };
})();
