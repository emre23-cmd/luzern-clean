from datetime import date, timedelta

import streamlit as st

st.set_page_config(page_title="Luzern Clean", page_icon="🧹")
st.title("Luzern Clean")
st.write("Plan a cleaning visit in the Lucerne area.")
st.info("Demo · Prices are illustrative. Requests are saved for this session only.")

SERVICES = {
    "Regular home cleaning": {"minimum_hours": 2, "hourly_rate": 45},
    "Deep cleaning": {"minimum_hours": 3, "hourly_rate": 55},
    "Move-out cleaning": {"minimum_hours": 4, "hourly_rate": 60},
}

AREAS = [
    "Luzern",
    "Meggen",
    "Greppen",
    "Weggis",
    "Vitznau",
    "Küssnacht am Rigi",
]

if "cleaning_requests" not in st.session_state:
    st.session_state.cleaning_requests = []

booking_tab, requests_tab = st.tabs(["Plan a cleaning", "My requests"])

with booking_tab:
    service = st.selectbox("Cleaning service", list(SERVICES))
    municipality = st.selectbox("Municipality", AREAS)
    minimum_hours = SERVICES[service]["minimum_hours"]
    hourly_rate = SERVICES[service]["hourly_rate"]

    hours = st.slider(
        "Estimated hours",
        min_value=minimum_hours,
        max_value=8,
        value=minimum_hours,
        key=f"hours_{service}",
    )

    estimated_price = hours * hourly_rate
    st.metric("Estimated price", f"CHF {estimated_price:,.0f}")
    st.caption(f"{hours} hours × CHF {hourly_rate} per hour")

    today = date.today()
    with st.form("cleaning_request"):
        preferred_date = st.date_input(
            "Preferred date",
            value=today + timedelta(days=1),
            min_value=today,
        )
        time_slot = st.selectbox("Preferred time", ["Morning", "Afternoon"])
        submitted = st.form_submit_button("Save demo request")

    if submitted:
        st.session_state.cleaning_requests.append(
            {
                "Service": service,
                "Municipality": municipality,
                "Date": preferred_date.isoformat(),
                "Time": time_slot,
                "Hours": hours,
                "Estimate (CHF)": estimated_price,
            }
        )
        st.success("Your demo request was saved. See it under My requests.")

with requests_tab:
    if st.session_state.cleaning_requests:
        st.table(list(reversed(st.session_state.cleaning_requests)))
    else:
        st.write("Your saved requests will appear here.")
