import streamlit as st
from utils.db import users_collection
from utils.sidebar import sidebar
from bson.objectid import ObjectId
from utils.data_processing import load_system_logs, load_user_logs, log_event

if not st.session_state.get("is_admin", False):
    st.error("You do not have permission to access this page.")
    st.stop()

# Hide Streamlit default elements
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            [data-testid="stSidebarNav"] {display: none;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def main():
    st.title("🛠️ Admin Dashboard")
    sidebar(current_page="🛠️ Admin Dashboard")

    st.markdown("""
    Welcome to the Admin Dashboard! Here you can manage users, view system logs, and perform administrative tasks.
    """)

    tab1, tab2, tab3 = st.tabs(["👥 Manage Users", "📜 View System Logs", "🍽️ View User Logs"])

    with tab1:
        user_management()

    with tab2:
        view_system_logs()

    with tab3:
        view_user_logs()

def user_management():
    st.subheader("User Management")

    users = list(users_collection.find({}))

    if not users:
        st.info("No users found in the database.")
        return
    
    for user in users:
        username = user.get("username", "N/A")
        email = user.get("email", "N/A")
        is_admin = user.get("is_admin", False)
        user_id = str(user["_id"])

        # Display user info
        col1, col2, col3, col4 = st.columns([2, 3, 2, 3])

        with col1:
            st.write(username)
        with col2:
            st.write(email)
        with col3:
            if is_admin:
                st.success("✅ Admin")
            else:
                st.error("❌ Not Admin")
        with col4:
            if not is_admin:
                promote_col, delete_col = st.columns(2)

                with promote_col:
                    if st.button(f"Promote", key=f"promote_{user_id}"):
                        st.session_state[f"pending_promote_{user_id}"] = True

                with delete_col:
                    if st.button(f"Delete", key=f"delete_{user_id}"):
                        st.session_state[f"pending_delete_{user_id}"] = True

        # handle pending actions outside buttons
        if st.session_state.get(f"pending_promote_{user_id}", False):
            st.warning(f"Are you sure you want to promote {username} to Admin?")

            confirm_col, cancel_col = st.columns(2)

            with confirm_col:
                if st.button(f"✅ Confirm", key=f"confirm_promote_{user_id}"):
                    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"is_admin": True}})
                    log_event("action", f"User {username} promoted to Admin.", user_id)
                    st.success(f"{username} has been promoted to Admin!")
                    st.session_state.pop(f"pending_promote_{user_id}", None)
                    del st.session_state[f"pending_promote_{user_id}"]
                    st.rerun()

            with cancel_col:
                if st.button(f"❌ Cancel", key=f"cancel_promote_{user_id}"):
                    del st.session_state[f"pending_promote_{user_id}"]
                    st.rerun()

        if st.session_state.get(f"pending_delete_{user_id}", False):
            st.error(f"⚠️ Are you sure you want to delete {username}? This cannot be undone.")

            confirm_col, cancel_col = st.columns(2)

            with confirm_col:
                if st.button(f"✅ Confirm", key=f"confirm_delete_{user_id}"):
                    users_collection.delete_one({"_id": ObjectId(user_id)})
                    log_event("action", f"User {username} deleted.", user_id)
                    st.success(f"{username} deleted successfully.")
                    del st.session_state[f"pending_delete_{user_id}"]
                    st.rerun()

            with cancel_col:
                if st.button(f"❌ Cancel", key=f"cancel_delete_{user_id}"):
                    del st.session_state[f"pending_delete_{user_id}"]
                    st.rerun()

    st.divider()

def view_system_logs():
    st.subheader("System Logs")
    
    # Filters
    log_type_filter = st.selectbox("Filter by Type", ["All", "Login", "Action"])
    search_keyword = st.text_input("Search logs...")
    limit = st.slider("Number of recent entries", key="system log slider", min_value=10, max_value=500, value=100)

    # Load logs from DB
    logs = load_system_logs()

    # Filter logs
    if log_type_filter != "All":
        logs = [log for log in logs if log["type"] == log_type_filter.lower()]
    if search_keyword:
        logs = [log for log in logs if search_keyword.lower() in log["message"].lower()]

    logs = logs[-limit:]  # Last N entries

    # Display
    for log in reversed(logs):
        st.markdown(f"""
        - **{log['timestamp']}**  
        {log['type'].upper()} ➔ {log['message']}
        """)

def view_user_logs():
    st.subheader("User Meal Logs")

    # Filter dropdown
    users = list(users_collection.find({}))
    user_options = [f"{user['username']} ({user['email']})" for user in users]
    
    selected_user = st.selectbox("Select a user to view meal logs:", options=user_options)
    limit = st.slider("Number of recent entries", key="user meal log slider", min_value=10, max_value=500, value=100)

    if selected_user:
        selected_username = selected_user.split(" (")[0]
        
        # Fetch meal logs
        user_logs = load_user_logs(selected_username, limit=limit)
        
        if user_logs:
            for log in reversed(user_logs):
                st.markdown(f"""
                - **{log['timestamp']}**  
                🍽️ {log['meal_name']} — *{log['calories']} kcal*
                """)
        else:
            st.info("No meal logs found for this user.")

if __name__ == "__main__":
    main()