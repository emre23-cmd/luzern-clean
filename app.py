from datetime import datetime, timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo

import streamlit as st


st.set_page_config(
    page_title="Luzern Clean",
    page_icon="🧹",
    layout="wide",
)

SERVICES = {
    "Regular home cleaning": {
        "name": "Regular home cleaning",
        "category": "ROUTINE CLEANING",
        "description": "Dusting, vacuuming, mopping, and a refresh of kitchens and bathrooms.",
        "minimum": 2,
        "rate": 45,
    },
    "Deep cleaning": {
        "name": "Deep cleaning",
        "category": "DETAILED CLEANING",
        "description": "A more thorough clean focused on buildup and hard-to-reach areas.",
        "minimum": 3,
        "rate": 55,
    },
    "Move-out cleaning": {
        "name": "Move-out cleaning",
        "category": "END OF TENANCY",
        "description": "A cleaning visit for an empty home before the handover.",
        "minimum": 4,
        "rate": 60,
    },
}

AREAS = ["Luzern", "Meggen", "Greppen", "Weggis", "Vitznau", "Küssnacht am Rigi"]
TIME_SLOTS = ["Morning · 08:00–12:00", "Afternoon · 13:00–17:00"]

st.session_state.setdefault("service", next(iter(SERVICES)))
st.session_state.setdefault("cleaning_requests", [])


def select_service(service_name):
    st.session_state.service = service_name


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Instrument+Serif&display=swap');

    .stApp { background: #f3f6f2; color: #163328; }
    [data-testid="stHeader"] { background: transparent; }
    .stApp, .stApp p, .stApp label { font-family: "DM Sans", sans-serif; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1140px;
        padding-top: 2.6rem;
        padding-bottom: 3rem;
    }
    [data-testid="stMainBlockContainer"] h2,
    [data-testid="stMainBlockContainer"] h3,
    [data-testid="stMainBlockContainer"] label,
    [data-testid="stCaptionContainer"] p { color: #163328; }

    .lc-hero {
        padding: clamp(26px, 5vw, 64px);
        border-radius: 28px;
        background:
            radial-gradient(ellipse at 92% 0%, #43795d 0%, transparent 56%),
            linear-gradient(130deg, #102d22, #1e513c);
        margin-bottom: 22px;
    }
    .lc-hero h1 {
        color: #f7faf4;
        font: 400 clamp(3.5rem, 7vw, 6.2rem)/0.96 "Instrument Serif", Georgia, serif;
        margin: 9px 0 16px;
        padding: 0;
    }
    .lc-hero p { color: #edf5eb; max-width: 42ch; margin: 0; }
    .lc-hero .lc-label { color: #c5ead2; }
    .lc-label {
        display: block;
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .12em;
    }
    .lc-card {
        min-height: 195px;
        padding: 19px;
        border-radius: 16px;
        border: 1px solid #d4e2d8;
        background: #fff;
        color: #163328;
    }
    .lc-card.selected { border-color: #528263; background: #e6f2e8; }
    .lc-card h3 { font-size: 1.12rem; margin: 9px 0 5px; padding: 0; }
    .lc-card p { margin: 0 0 10px; font-size: .92rem; line-height: 1.45; }
    .lc-card strong { color: #25543b; }
    .lc-quote {
        padding: 23px;
        border-radius: 16px;
        background: #15382a;
        color: #f7faf4;
    }
    .lc-quote .lc-label { color: #c5ead2; }
    .lc-quote .lc-price {
        font: 400 3.25rem/1 "Instrument Serif", Georgia, serif;
        margin: 9px 0;
    }
    .lc-quote p { color: #edf5eb; margin: 0; }
    .stButton button[kind="primary"],
    .stFormSubmitButton button[kind="primary"] {
        background: #225640;
        color: #fff;
        border-color: #225640;
    }
    </style>
    <div class="lc-hero">
        <span class="lc-label">HOME CLEANING IN THE LUCERNE AREA</span>
        <h1>Luzern Clean</h1>
        <p>Choose a cleaning service, get an estimate in CHF, and tell us when you’d like a visit.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Demo · Rates are illustrative. Requests stay in this session.")

booking_tab, requests_tab = st.tabs(
    ["Book a cleaning", f"My requests ({len(st.session_state.cleaning_requests)})"]
)

with booking_tab:
    st.subheader("Choose a service")
    card_columns = st.columns(len(SERVICES), gap="medium")

    for column, (service_name, service) in zip(card_columns, SERVICES.items()):
        selected = st.session_state.service == service_name
        with column:
            st.markdown(
                f"""
                <div class="lc-card{' selected' if selected else ''}">
                    <span class="lc-label">{service['category']}</span>
                    <h3>{service['name']}</h3>
                    <p>{service['description']}</p>
                    <strong>CHF {service['rate']} / hour</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button(
                "Selected" if selected else f"Choose {service['name'].lower()}",
                key=f"service_{service_name}",
                disabled=selected,
                type="primary" if selected else "secondary",
                width="stretch",
                on_click=select_service,
                args=(service_name,),
            )

    st.divider()
    details, summary = st.columns([3, 2], gap="large")
    service_name = st.session_state.service
    service = SERVICES[service_name]

    with details:
        st.subheader("Visit details")
        municipality = st.selectbox("Municipality", AREAS)
        hours = st.slider(
            "Estimated duration (hours)",
            min_value=service["minimum"],
            max_value=8,
            value=service["minimum"],
            key=f"hours_{service_name}",
        )

    estimate = hours * service["rate"]
    with summary:
        st.subheader("Price estimate")
        st.markdown(
            f"""
            <div class="lc-quote">
                <span class="lc-label">{service['name'].upper()}</span>
                <div class="lc-price">CHF {estimate:,.0f}</div>
                <p>{hours} hours × CHF {service['rate']} per hour</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Final scope and price would be confirmed before the visit.")

    today = datetime.now(ZoneInfo("Europe/Zurich")).date()

    with st.form("cleaning_request"):
        st.subheader("When would you like a visit?")
        date_column, time_column = st.columns(2)

        with date_column:
            preferred_date = st.date_input(
                "Preferred date",
                value=today + timedelta(days=1),
                min_value=today,
                format="DD.MM.YYYY",
            )

        with time_column:
            time_slot = st.selectbox("Preferred time", TIME_SLOTS)

        submitted = st.form_submit_button(
            "Save demo request",
            type="primary",
            width="stretch",
        )

    if submitted:
        if preferred_date is None or preferred_date < today:
            st.error("Choose today or a later date.")
        else:
            request = {
                "reference": uuid4().hex[:8].upper(),
                "service": service_name,
                "municipality": municipality,
                "date": preferred_date.strftime("%d.%m.%Y"),
                "time": time_slot,
                "hours": hours,
                "estimate": estimate,
                "status": "Saved",
            }
            st.session_state.cleaning_requests.append(request)
            st.session_state.notice = (
                f"Request {request['reference']} saved. Find it under My requests."
            )
            st.rerun()

    notice = st.session_state.pop("notice", None)
    if notice:
        st.success(notice)

with requests_tab:
    st.subheader("My requests")

    if not st.session_state.cleaning_requests:
        st.info("Your saved demo requests will appear here.")

    for request in reversed(st.session_state.cleaning_requests):
        with st.container(border=True):
            visit, price = st.columns([3, 1])
            with visit:
                st.markdown(f"**{request['service']}** · {request['municipality']}")
                st.write(f"{request['date']} · {request['time']} · {request['hours']} hours")
                st.caption(f"Reference {request['reference']} · {request['status']}")

            with price:
                st.markdown(f"**CHF {request['estimate']:,.0f}**")
                if request["status"] == "Saved" and st.button(
                    "Cancel request", key=f"cancel_{request['reference']}"
                ):
                    request["status"] = "Cancelled"
                    st.rerun()

    st.caption("Demo requests are stored for the current session.")
