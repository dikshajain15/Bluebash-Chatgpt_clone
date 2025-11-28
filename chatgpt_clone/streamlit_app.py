import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="ChatGPT Clone", page_icon="🤖", layout="wide")

# ---------------------------------------------------
# Helper: API Request Wrapper
# ---------------------------------------------------
def api_post(endpoint, data=None, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.post(f"{API_BASE}{endpoint}", json=data, headers=headers)


def api_get(endpoint, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.get(f"{API_BASE}{endpoint}", headers=headers)


# ---------------------------------------------------
# Sidebar (Login + Logout + Sessions)
# ---------------------------------------------------
with st.sidebar:
    st.title("🔐 Authentication")

    # If not logged in → Show login UI
    if "token" not in st.session_state:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            resp = api_post("/auth/login", {"username": username, "password": password})
            if resp.status_code == 200:
                st.session_state["token"] = resp.json()["access_token"]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials.")

    # If already logged in:
    else:
        st.success("Logged in ✔")

        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.divider()
        st.subheader("📚 Your Chat Sessions")

        # Fetch all sessions
        sessions = api_get("/sessions/all", st.session_state["token"])

        if sessions.status_code == 200:
            session_list = sessions.json()
            session_ids = [s["id"] for s in session_list]

            if session_list:
                selected = st.selectbox(
                    "Choose session:",
                    session_ids,
                    format_func=lambda x: f"Session {x}"
                )
                st.session_state["session_id"] = selected
            else:
                st.write("No sessions yet.")
        else:
            st.write("Failed to load sessions.")


# ---------------------------------------------------
# Main Area
# ---------------------------------------------------
st.title("🤖 ChatGPT Clone")

# Require login
if "token" not in st.session_state:
    st.warning("Please login from the sidebar.")
    st.stop()

# ---------------------------------------------------
# Create new session button
# ---------------------------------------------------
if st.button("➕ Start New Session"):
    resp = api_post("/sessions/", token=st.session_state["token"])
    if resp.status_code == 200:
        st.session_state["session_id"] = resp.json()["id"]
        st.success(f"New session created! ID: {st.session_state['session_id']}")
        st.rerun()
    else:
        st.error("Failed to create session.")

# Make sure a session is selected
if "session_id" not in st.session_state:
    st.info("Start a new session or choose one from the sidebar.")
    st.stop()

session_id = st.session_state["session_id"]
st.write(f"### 📌 Current Session: **{session_id}**")


# ---------------------------------------------------
# Load chat history
# ---------------------------------------------------
history = api_get(f"/sessions/{session_id}/chats", st.session_state["token"])

if history.status_code == 200:
    chats = history.json()

    for chat in chats:
        if chat["role"] == "user":
            st.chat_message("user").markdown(chat["content"])
        else:
            st.chat_message("assistant").markdown(chat["content"])
else:
    st.error("Failed to load chat history.")


# ---------------------------------------------------
# User input
# ---------------------------------------------------
user_msg = st.chat_input("Type your message...")

if user_msg:
    resp = api_post(
        "/chat/message",
        data={
            "session_id": session_id,
            "message": user_msg
        },
        token=st.session_state["token"]
    )

    if resp.status_code == 200:
        reply = resp.json()["content"]
        st.chat_message("assistant").markdown(reply)
    else:
        st.error("❌ Error sending message")
