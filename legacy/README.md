# Legacy prototype

`pythonproject.py` in this folder is the original Tkinter desktop prototype of Interactive Geo
Explorer. It's kept for historical reference only and is **not** maintained.

It has been superseded by the Streamlit app at the repo root (`app.py`), which fixes the issues
found in this prototype:

- **Pixel-coordinate map clicks → real lat/long markers.** The original app matched mouse clicks
  against a hardcoded dict of pixel rectangles tuned for one screen size, so clicks misaligned on
  any other resolution. The new app uses real geographic coordinates with Folium markers.
- **Plaintext MySQL passwords → bcrypt-hashed SQLite.** The original app stored user passwords as
  plaintext in a local MySQL database. The new app hashes passwords with bcrypt and uses a
  bundled SQLite database, so there's no external database server to install.
- **Desktop-only → deployable web app.** The new app runs in a browser and can be deployed for
  free on Streamlit Community Cloud.

To run this legacy prototype, you'd need a local MySQL server (`geography_db`) and the packages
imported at the top of the file (`pillow`, `openai`, `mysql-connector-python`).
