import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Load CSV files ---
USERS_CSV = "users.csv"
COMMENTS_CSV = "comments.csv"
DONATIONS_CSV = "donations.csv"
FEEDBACK_CSV = "feedback.csv"
NEEDS_CSV = "needs.csv"
VOLUNTEERS_CSV = "volunteers.csv"
CAMPAIGNS_CSV = "campaigns.csv"

# Create CSVs if not exist
def init_csv(file, columns):
    if not os.path.exists(file):
        pd.DataFrame(columns=columns).to_csv(file, index=False)

init_csv(USERS_CSV, ["username", "password", "role", "location"])
init_csv(COMMENTS_CSV, ["user", "ngo_id", "message", "timestamp"])
init_csv(DONATIONS_CSV, ["user", "ngo_id", "amount", "timestamp"])
init_csv(FEEDBACK_CSV, ["user", "message", "timestamp"])
init_csv(NEEDS_CSV, ["ngo_id", "item", "description", "location", "date_posted"])
init_csv(VOLUNTEERS_CSV, ["ngo_id", "role", "description", "location", "date_posted"])
init_csv(CAMPAIGNS_CSV, ["ngo_id", "title", "goal", "raised", "deadline", "description"])

# --- Page Setup ---
st.set_page_config(page_title="NGO Donation App", layout="wide")

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- Header UI Styling ---
def styled_header(title):
    st.markdown(f"""
        <h2 style='text-align: center; color: #2E8B57;'>{title}</h2>
    """, unsafe_allow_html=True)

# --- Login / Registration ---
def login_page():
    styled_header("Welcome to the NGO Donation & Volunteering App")
    st.write("Please login or register to continue.")
    
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        role = st.selectbox("Login as", ["Donor/Volunteer", "Organisation", "Admin"], key="login_role")

        if st.button("Login"):
            df = pd.read_csv(USERS_CSV)
            user = df[(df.username == username) & (df.password == password) & (df.role == role)]
            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = role
                st.success("Logged in successfully!")
            else:
                st.warning("Invalid credentials or role. Please register.")

    with tab2:
        new_user = st.text_input("New Username", key="reg_user")
        new_pass = st.text_input("New Password", type="password", key="reg_pass")
        new_role = st.selectbox("Register as", ["Donor/Volunteer", "Organisation"], key="reg_role")
        new_location = st.text_input("Location", key="reg_loc")

        if st.button("Register"):
            df = pd.read_csv(USERS_CSV)
            if new_user in df.username.values:
                st.warning("Username already exists.")
            else:
                new_row = pd.DataFrame([[new_user, new_pass, new_role, new_location]], columns=df.columns)
                new_row.to_csv(USERS_CSV, mode='a', header=False, index=False)
                st.success("Registration successful. You can now login.")

# Function to sanitize inputs by removing commas
def sanitize_input(data):
    return data.replace(",", "")  # You can replace with another character if necessary

# --- Main Dashboard ---
def dashboard():
    role = st.session_state.role
    username = st.session_state.username

    styled_header(f"Dashboard: {role}")

    if role == "Donor/Volunteer":
        donor_dashboard(username)
    elif role == "Organisation":
        organisation_dashboard(username)
    elif role == "Admin":
        admin_dashboard()

# --- Donor Dashboard ---
def donor_dashboard(user):
    st.subheader("Explore NGOs & Campaigns")
    
    orgs = pd.read_csv(USERS_CSV)
    needs = pd.read_csv(NEEDS_CSV)
    vols = pd.read_csv(VOLUNTEERS_CSV)

    # Debugging: Check the first few rows of orgs
    st.write(f"Organizations Data Preview:\n{orgs.head()}")
    
    # Ensure there is a 'role' column and it's set correctly
    if 'role' not in orgs.columns:
        st.error("Role column missing in the organizations CSV!")
    else:
        st.write(f"Roles in organizations:\n{orgs['role'].unique()}")

    # Location and keyword filters from donor
    location_filter = st.text_input("Search by Location", key="loc_filter")
    keyword_filter = st.text_input("Search Needs (e.g., food, books)", key="kw_filter")
    show_vols = st.checkbox("Only show organisations with open volunteerships")

    # Filter organizations where the role is "Organisation"
    filtered_orgs = orgs[orgs.role == "Organisation"]

    # Display all organizations first, before applying any filters
    st.write(f"Total organizations before filters: {len(filtered_orgs)}")

    # Display organizations and their needs first (no filters applied)
    for _, row in filtered_orgs.iterrows():
        with st.expander(f"{row.username} ({row.location})"):
            st.write(f"{row.username} needs: ")
            st.dataframe(needs[needs.ngo_id == row.username][["item", "description", "date_posted"]])
            st.write("Volunteerships:")
            st.dataframe(vols[vols.ngo_id == row.username][["role", "description", "date_posted"]])

            st.text_area("Send a message:", key=f"msg_{row.username}")
            if st.button("Send", key=f"send_{row.username}"):
                msg = sanitize_input(st.session_state[f"msg_{row.username}"])  # Sanitize the message
                new = pd.DataFrame([[user, row.username, msg, datetime.now().isoformat()]], columns=["user", "ngo_id", "message", "timestamp"])
                new.to_csv(COMMENTS_CSV, mode='a', header=False, index=False)
                st.success("Message sent!")

            if st.button("Donate", key=f"donate_{row.username}_{row.name}"):
                if st.button("Donate", key=f"donate_{row.username}"):
                    new = pd.DataFrame([[user, row.username, amount, datetime.now().isoformat()]], columns=["user", "ngo_id", "amount", "timestamp"])
                    new.to_csv(DONATIONS_CSV, mode='a', header=False, index=False)
                    st.success("Donation successful!")

    # Apply location filter if provided
    if location_filter:
        filtered_orgs = filtered_orgs[filtered_orgs.location.str.contains(location_filter, case=False, na=False)]
        st.write(f"Organizations after location filter: {len(filtered_orgs)}")

    # Apply keyword filter if provided
    if keyword_filter:
        needs_filtered = needs[needs.item.str.contains(keyword_filter, case=False, na=False)]
        filtered_orgs = filtered_orgs[filtered_orgs.username.isin(needs_filtered.ngo_id)]
        st.write(f"Organizations after keyword filter: {len(filtered_orgs)}")

    # Show only organizations with open volunteerships if checked
    if show_vols:
        filtered_orgs = filtered_orgs[filtered_orgs.username.isin(vols.ngo_id)]
        st.write(f"Organizations after volunteership filter: {len(filtered_orgs)}")

    # After applying all filters, display the remaining organizations
    if len(filtered_orgs) == 0:
        st.write("No organizations match the current filters.")
    else:
        for _, row in filtered_orgs.iterrows():
            with st.expander(f"{row.username} ({row.location})"):
                st.write(f"{row.username} needs: ")
                st.dataframe(needs[needs.ngo_id == row.username][["item", "description", "date_posted"]])
                st.write("Volunteerships:")
                st.dataframe(vols[vols.ngo_id == row.username][["role", "description", "date_posted"]])

                st.text_area("Send a message:", key=f"msg_{row.username}_{row.name}")
                if st.button("Send", key=f"send_{row.username}_{row.name}"):
                    msg = sanitize_input(st.session_state[f"msg_{row.username}"])  # Sanitize the message
                    new = pd.DataFrame([[user, row.username, msg, datetime.now().isoformat()]], columns=["user", "ngo_id", "message", "timestamp"])
                    new.to_csv(COMMENTS_CSV, mode='a', header=False, index=False)
                    st.success("Message sent!")

                amount = st.number_input("Donate Amount", min_value=1, key=f"amt_{row.username}")
                if st.button("Donate", key=f"donate_{row.username}"):
                    new = pd.DataFrame([[user, row.username, amount, datetime.now().isoformat()]], columns=["user", "ngo", "amount", "timestamp"])
                    new.to_csv(DONATIONS_CSV, mode='a', header=False, index=False)
                    st.success("Donation successful!")

# --- Organisation Dashboard ---
def organisation_dashboard(org):
    needs = pd.read_csv(NEEDS_CSV)
    st.subheader("Manage Your Needs")

    st.write("### Add a new need")
    item = st.text_input("Item")
    desc = st.text_area("Description")
    
    # Sanitize inputs before adding
    if st.button("Add Need"):
        item = sanitize_input(item)
        desc = sanitize_input(desc)
        
        if item and desc:  # Ensure both fields are filled
            row = pd.DataFrame([[org, item, desc, "", datetime.now().date()]], columns=needs.columns)
            row.to_csv(NEEDS_CSV, mode='a', header=False, index=False)
            st.success("Need added.")
        else:
            st.warning("Please fill in both fields.")
    
    st.write("### Your Needs")
    
    # Display the needs for the organization with date_posted and current_status
    needs_data = needs[needs.ngo_id == org][["item", "description", "date_posted", "current_status"]]
    st.dataframe(needs_data)

    comments = pd.read_csv(COMMENTS_CSV)
    st.write("### Messages Received")
    st.dataframe(comments[comments.ngo_id == org])



# --- Admin Dashboard ---
def admin_dashboard():
    users = pd.read_csv(USERS_CSV)
    donations = pd.read_csv(DONATIONS_CSV)
    feedback = pd.read_csv(FEEDBACK_CSV)
    needs = pd.read_csv(NEEDS_CSV)

    st.write("### App Analytics")
    st.metric("Total Users", len(users))
    st.metric("Total Donations", donations.amount.sum())
    st.metric("Total NGOs", len(users[users.role == "Organisation"]))

    st.write("### Feedback from Users")
    st.dataframe(feedback)

# --- App Router ---
if not st.session_state.logged_in:
    login_page()
else:
    dashboard()
