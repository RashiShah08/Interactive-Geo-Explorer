# Legacy: Streamlit version

The second iteration of Interactive Geo Explorer — a Streamlit app using Folium for maps.
Kept for reference only; the live version is the FastAPI app at the repository root.

What it got right, and what the current version carries forward:

- Replaced the original Tkinter app's hardcoded pixel-rectangle click detection with real
  latitude/longitude markers.
- Replaced plaintext MySQL password storage with bcrypt hashing over SQLite.
- Established that CartoDB's dark map tiles now require a paid API key, and that OSM tiles
  plus a CSS filter are the reliable keyless alternative.

Why it was replaced: Streamlit re-runs the entire script on every interaction, which makes
fine-grained UI state (marker selection, an open chat panel, view transitions) awkward, and
its widget styling is difficult to move away from. The current version serves a JSON API to
a hand-written frontend instead.

To run it you would need `streamlit`, `streamlit-folium` and `folium`, none of which are in
the current `requirements.txt`.
