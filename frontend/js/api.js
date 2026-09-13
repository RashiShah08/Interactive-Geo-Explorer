const API = (() => {
  async function request(path, options = {}) {
    const response = await fetch(path, {
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      ...options,
    });

    let body = null;
    try {
      body = await response.json();
    } catch {
      body = null;
    }

    return { status: response.status, ok: response.ok, body };
  }

  const post = (path, payload) =>
    request(path, { method: "POST", body: JSON.stringify(payload) });

  return {
    signup: (username, password) => post("/api/signup", { username, password }),
    login: (username, password) => post("/api/login", { username, password }),
    logout: () => post("/api/logout", {}),
    me: () => request("/api/me"),
    worldPlaces: () => request("/api/places/world"),
    indiaPlaces: () => request("/api/places/india"),
    chat: (messages) => post("/api/chat", { messages }),
  };
})();
