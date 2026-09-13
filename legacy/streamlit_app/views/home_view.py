import streamlit as st


def render_home() -> None:
    username = st.session_state.get("username", "")
    st.markdown(f"### Welcome, {username} 👋")
    st.write("Pick a map to start exploring.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='geo-card'>", unsafe_allow_html=True)
        st.image("world_map.jpg", use_container_width=True)
        st.markdown("<div class='geo-title'>World Map</div>", unsafe_allow_html=True)
        st.write("Click markers to explore famous places by continent.")
        if st.button("Explore Continents", key="go_world"):
            st.session_state["view"] = "world_map"
            st.session_state["selected_place"] = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='geo-card'>", unsafe_allow_html=True)
        st.image("india_map.jpg", use_container_width=True)
        st.markdown("<div class='geo-title'>India Map</div>", unsafe_allow_html=True)
        st.write("Click markers to view world records by state.")
        if st.button("Explore India", key="go_india"):
            st.session_state["view"] = "india_map"
            st.session_state["selected_place"] = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    if st.button("Log out"):
        for key in ("authenticated", "username", "view", "selected_place", "chat_history"):
            st.session_state.pop(key, None)
        st.rerun()
