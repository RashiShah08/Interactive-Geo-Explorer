const Auth = (() => {
  let mode = "login";
  let onSignedIn = () => {};

  const form = () => document.getElementById("auth-form");
  const usernameInput = () => document.getElementById("auth-username");
  const passwordInput = () => document.getElementById("auth-password");
  const messageEl = () => document.getElementById("auth-message");
  const submitBtn = () => document.getElementById("auth-submit");

  function setMessage(text, kind = "error") {
    const el = messageEl();
    el.textContent = text;
    el.classList.toggle("is-ok", kind === "ok");
  }

  function moveTabMarker() {
    const active = document.querySelector(".tab.is-active");
    const marker = document.querySelector(".tab-marker");
    if (!active || !marker) return;
    marker.style.width = `${active.offsetWidth}px`;
    marker.style.transform = `translateX(${active.offsetLeft}px)`;
  }

  function setMode(next, { animate = false } = {}) {
    mode = next;
    document.querySelectorAll(".tab").forEach((tab) => {
      tab.classList.toggle("is-active", tab.dataset.mode === next);
    });

    if (animate) {
      const node = form();
      node.classList.remove("is-swapping");
      void node.offsetWidth;
      node.classList.add("is-swapping");
    }
    submitBtn().querySelector(".btn-text").textContent =
      next === "login" ? "Sign in" : "Create account";
    passwordInput().setAttribute(
      "autocomplete",
      next === "login" ? "current-password" : "new-password"
    );
    setMessage("");
    moveTabMarker();
  }

  function setBusy(busy) {
    const btn = submitBtn();
    btn.disabled = busy;
    btn.classList.toggle("is-busy", busy);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const username = usernameInput().value.trim();
    const password = passwordInput().value;

    if (!username || !password) {
      setMessage("Enter both a username and a password.");
      return;
    }

    setBusy(true);
    try {
      if (mode === "signup") {
        const { ok, body } = await API.signup(username, password);
        if (!ok) {
          setMessage(body?.message || "Could not create that account.");
          return;
        }
        setMode("login", { animate: true });
        setMessage("Account created. Sign in to continue.", "ok");
        passwordInput().value = "";
        usernameInput().value = username;
        return;
      }

      const { ok, body } = await API.login(username, password);
      if (!ok) {
        setMessage(body?.message || "Invalid username or password.");
        return;
      }
      form().reset();
      setMessage("");
      onSignedIn(body.username);
    } catch {
      setMessage("Could not reach the server. Is it still running?");
    } finally {
      setBusy(false);
    }
  }

  function init(signedInCallback) {
    onSignedIn = signedInCallback;
    document.querySelectorAll(".tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        if (tab.dataset.mode !== mode) setMode(tab.dataset.mode, { animate: true });
      });
    });
    form().addEventListener("submit", handleSubmit);
    window.addEventListener("resize", moveTabMarker);
    setMode("login");
    // Fonts load after first paint and change tab widths; re-measure once ready.
    if (document.fonts?.ready) document.fonts.ready.then(moveTabMarker);
  }

  return { init, focus: () => usernameInput()?.focus() };
})();
