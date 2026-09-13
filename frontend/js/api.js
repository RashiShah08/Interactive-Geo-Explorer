const API = (() => {
  async function request(path, options = {}) {
    const response = await fetch(path, {
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

  return {
    worldPlaces: () => request("/api/places/world"),
    indiaPlaces: () => request("/api/places/india"),
    chat: (messages) =>
      request("/api/chat", { method: "POST", body: JSON.stringify({ messages }) }),
  };
})();
