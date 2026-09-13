import streamlit as st
from openai import OpenAIError

from src.chatbot.client import get_api_key, get_reply


def render_chat() -> None:
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("chat_error", None)

    st.markdown("#### 🤖 Smart Chatbot")

    seed = st.session_state.pop("chat_seed_prompt", None)
    if seed:
        st.session_state["chat_history"].append({"role": "user", "content": seed})

    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if not get_api_key():
        st.error("OPENAI_API_KEY not configured — set it in .env or Streamlit secrets.")
        return

    needs_reply = (
        st.session_state["chat_history"]
        and st.session_state["chat_history"][-1]["role"] == "user"
    )
    if needs_reply:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    reply = get_reply(st.session_state["chat_history"])
                    st.session_state["chat_error"] = None
                except OpenAIError as exc:
                    reply = None
                    st.session_state["chat_error"] = str(exc)
                    st.error(f"Error: could not get a response ({exc}).")
            if reply:
                st.markdown(reply)
                st.session_state["chat_history"].append({"role": "assistant", "content": reply})

    if st.session_state["chat_error"]:
        if st.button("Try again"):
            st.session_state["chat_error"] = None
            st.rerun()

    if prompt := st.chat_input("Ask about any place..."):
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear conversation"):
            st.session_state["chat_history"] = []
            st.session_state["chat_error"] = None
            st.rerun()
    with col2:
        st.feedback("stars", key="chat_rating")
