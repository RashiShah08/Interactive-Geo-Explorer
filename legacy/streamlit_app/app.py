from dotenv import load_dotenv
import streamlit as st

from src.data.india_states import INDIA_STATES
from src.data.world_landmarks import WORLD_LANDMARKS
from src.ui.theme import inject_theme
from views.auth_view import render_auth
from views.chat_view import render_chat
from views.home_view import render_home
from views.map_view import render_map

load_dotenv()

st.set_page_config(page_title="Interactive Geo Explorer", page_icon="🌍", layout="wide")
inject_theme()

st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("view", "home")
st.session_state.setdefault("selected_place", None)
st.session_state.setdefault("show_chat", False)

if not st.session_state["authenticated"]:
    render_auth()
    st.stop()

view = st.session_state["view"]

if view == "home":
    render_home()
elif view == "world_map":
    render_map(
        WORLD_LANDMARKS,
        title="World Map",
        center=(20, 0),
        zoom_start=2,
        seed_prompt_country=None,
    )
elif view == "india_map":
    render_map(
        INDIA_STATES,
        title="India Map",
        center=(22.5, 80),
        zoom_start=5,
        seed_prompt_country="India",
    )

with st.sidebar:
    st.markdown("### 💬 Chatbot")
    if st.button("Open standalone chatbot"):
        st.session_state["show_chat"] = True
    if st.session_state["show_chat"]:
        render_chat()
        if st.button("Close chatbot"):
            st.session_state["show_chat"] = False
            st.rerun()
