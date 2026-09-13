import streamlit as st
from streamlit_folium import st_folium

from src.data.models import GeoPlace
from src.ui.map_builder import build_map


def render_map(
    places: list[GeoPlace],
    title: str,
    center: tuple[float, float],
    zoom_start: int,
    seed_prompt_country: str | None,
) -> None:
    top_left, top_right = st.columns([5, 1])
    with top_left:
        st.markdown(f"### {title}")
    with top_right:
        if st.button("⬅ Back"):
            st.session_state["view"] = "home"
            st.session_state["selected_place"] = None
            st.rerun()

    categories = sorted({place.category for place in places})
    selected_categories = st.multiselect(
        "Filter by category", categories, default=categories, key=f"filter_{title}"
    )
    filtered_places = [p for p in places if p.category in selected_categories]

    map_col, detail_col = st.columns([2, 1])

    with map_col:
        fmap = build_map(filtered_places, center=center, zoom_start=zoom_start)
        map_data = st_folium(
            fmap,
            width=None,
            height=600,
            returned_objects=["last_object_clicked_tooltip"],
            key=f"folium_{title}",
        )

        clicked_tooltip = map_data.get("last_object_clicked_tooltip")
        if clicked_tooltip:
            match = next((p for p in filtered_places if p.title == clicked_tooltip), None)
            if match:
                st.session_state["selected_place"] = match

    with detail_col:
        place = st.session_state.get("selected_place")
        if place and place in filtered_places:
            st.markdown("<div class='geo-card'>", unsafe_allow_html=True)
            st.image(place.image_file, use_container_width=True)
            st.markdown(f"<div class='geo-title'>{place.title}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='geo-description'>{place.description}</div>", unsafe_allow_html=True)
            if st.button("💬 Ask chatbot about this", key=f"ask_{place.key}"):
                st.session_state["chat_seed_prompt"] = (
                    f"Provide a concise overview of {place.title} based on this context: "
                    f"{place.description}."
                )
                st.session_state["chat_seed_country"] = seed_prompt_country
                st.session_state["show_chat"] = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Click a marker on the map to see details here.")
