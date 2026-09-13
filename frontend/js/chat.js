const Chat = (() => {
  const SUGGESTIONS = [
    "How far is the Eiffel Tower from the Colosseum?",
    "What's in South India?",
    "The tallest sandcastle",
  ];

  let history = [];
  let pending = false;
  let onCitation = () => {};

  const panel = () => document.getElementById("chat-panel");
  const log = () => document.getElementById("chat-log");
  const input = () => document.getElementById("chat-input");
  const sendBtn = () => document.getElementById("chat-send");
  const suggestionBar = () => document.getElementById("chat-suggestions");

  const scrollToEnd = () => { log().scrollTop = log().scrollHeight; };
  const isOpen = () => panel().classList.contains("is-open");

  function renderSuggestions() {
    const bar = suggestionBar();
    bar.innerHTML = "";
    if (history.length) { bar.classList.add("is-hidden"); return; }

    bar.classList.remove("is-hidden");
    SUGGESTIONS.forEach((text) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "suggestion";
      chip.textContent = text;
      chip.addEventListener("click", () => send(text));
      bar.appendChild(chip);
    });
  }

  function bubble(role, text, { isError = false } = {}) {
    const wrap = document.createElement("div");
    wrap.className = `msg is-${role === "user" ? "user" : "bot"}${isError ? " is-error" : ""}`;

    const label = document.createElement("span");
    label.className = "msg-role";
    label.textContent = role === "user" ? "You" : "Guide";

    const body = document.createElement("div");
    body.className = "msg-body";
    body.textContent = text;

    wrap.append(label, body);
    log().appendChild(wrap);
    scrollToEnd();
    return wrap;
  }

  /** Every answer comes from specific records; let people jump straight to them. */
  function attachCitations(node, citations) {
    if (!citations.length) return;

    const strip = document.createElement("div");
    strip.className = "cites";

    const label = document.createElement("span");
    label.className = "cites-label";
    label.textContent = "From";
    strip.appendChild(label);

    citations.forEach((citation) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "cite";
      chip.textContent = citation.title;
      chip.addEventListener("click", () => onCitation(citation.atlas, citation.key));
      strip.appendChild(chip);
    });

    node.appendChild(strip);
    scrollToEnd();
  }

  function typingBubble() {
    const wrap = document.createElement("div");
    wrap.className = "msg is-bot";
    wrap.innerHTML =
      '<span class="msg-role">Guide</span>' +
      '<div class="msg-body"><span class="typing"><span></span><span></span><span></span></span></div>';
    log().appendChild(wrap);
    scrollToEnd();
    return wrap;
  }

  function setPending(value) {
    pending = value;
    sendBtn().disabled = value;
    input().disabled = value;
  }

  async function exchange() {
    setPending(true);
    const typing = typingBubble();

    try {
      const { ok, body } = await API.chat(history);
      typing.remove();

      if (!ok) {
        const failure = bubble("bot", body?.message || "The guide could not answer.", { isError: true });
        const retry = document.createElement("button");
        retry.className = "msg-retry";
        retry.type = "button";
        retry.textContent = "Try again";
        retry.addEventListener("click", () => { failure.remove(); exchange(); });
        failure.querySelector(".msg-body").appendChild(retry);
        return;
      }

      history.push({ role: "assistant", content: body.reply });
      const node = bubble("assistant", body.reply);
      attachCitations(node, body.citations || []);
    } catch {
      typing.remove();
      bubble("bot", "Could not reach the server.", { isError: true });
    } finally {
      setPending(false);
      if (isOpen()) input().focus();
    }
  }

  function send(text) {
    const message = text.trim();
    if (!message || pending) return;
    history.push({ role: "user", content: message });
    bubble("user", message);
    renderSuggestions();
    exchange();
  }

  function open() {
    panel().classList.add("is-open");
    panel().setAttribute("aria-hidden", "false");
    document.getElementById("chat-fab").classList.add("is-hidden");
    renderSuggestions();
    if (!pending) input().focus();
    scrollToEnd();
  }

  function close() {
    panel().classList.remove("is-open");
    panel().setAttribute("aria-hidden", "true");
    document.getElementById("chat-fab").classList.remove("is-hidden");
  }

  function askAbout(place) {
    open();
    send(`Tell me about ${place.title}`);
  }

  function clear() {
    history = [];
    log().innerHTML = "";
    renderSuggestions();
  }

  function reset() {
    clear();
    close();
  }

  function init({ onCitation: citationCallback } = {}) {
    if (citationCallback) onCitation = citationCallback;

    // The floating launcher plus its narrow-screen stand-ins in each toolbar.
    ["chat-fab", "map-chat", "home-chat"].forEach((id) => {
      document.getElementById(id)?.addEventListener("click", open);
    });
    document.getElementById("chat-close").addEventListener("click", close);
    document.getElementById("chat-clear").addEventListener("click", () => {
      clear();
      input().focus();
    });
    document.getElementById("chat-form").addEventListener("submit", (event) => {
      event.preventDefault();
      const value = input().value;
      input().value = "";
      send(value);
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && isOpen() && !Palette.isOpen()) close();
    });
    renderSuggestions();
  }

  return { init, askAbout, reset, close };
})();
