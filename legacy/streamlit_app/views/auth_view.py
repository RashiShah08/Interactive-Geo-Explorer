import streamlit as st

from src.auth.service import login, signup


def render_auth() -> None:
    st.session_state.setdefault("auth_mode", "login")

    st.markdown("<div class='geo-card'>", unsafe_allow_html=True)
    st.markdown("<div class='geo-title'>🌍 Interactive Geo Explorer</div>", unsafe_allow_html=True)

    if st.session_state["auth_mode"] == "login":
        _render_login()
    else:
        _render_signup()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_login() -> None:
    st.subheader("Login")
    success_message = st.session_state.pop("signup_success_message", None)
    if success_message:
        st.success(success_message)
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        ok, message = login(username, password)
        if ok:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username.strip()
            st.rerun()
        else:
            st.error(message)

    st.caption("Don't have an account?")
    if st.button("Sign up instead"):
        st.session_state["auth_mode"] = "signup"
        st.rerun()


def _render_signup() -> None:
    st.subheader("Sign Up")
    with st.form("signup_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign Up")

    if submitted:
        ok, message = signup(username, password)
        if ok:
            st.session_state["auth_mode"] = "login"
            st.session_state["signup_success_message"] = message
            st.rerun()
        else:
            st.error(message)

    st.caption("Already have an account?")
    if st.button("Log in instead"):
        st.session_state["auth_mode"] = "login"
        st.rerun()
