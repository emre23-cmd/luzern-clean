from datetime import datetime, time, timedelta
from urllib.parse import urlencode
from uuid import uuid4
from zoneinfo import ZoneInfo

import streamlit as st


st.set_page_config(page_title="Luzern Clean", page_icon="🧹", layout="wide")

ZURICH = ZoneInfo("Europe/Zurich")
AREAS = {
    "Luzern": (47.0502, 8.3093),
    "Meggen": (47.0465, 8.3740),
    "Greppen": (47.0561, 8.4299),
    "Weggis": (47.0321, 8.4337),
    "Vitznau": (47.0106, 8.4839),
    "Küssnacht am Rigi": (47.0830, 8.4410),
}

SERVICES = {
    "Regular home cleaning": (
        2, 45, "Routine upkeep for kitchens, bathrooms, floors, and surfaces."
    ),
    "Deep cleaning": (
        3, 55, "Detailed cleaning for buildup and hard-to-reach areas."
    ),
    "Move-out cleaning": (
        4, 60, "Cleaning for an empty home before the handover."
    ),
}

ADD_ONS = {
    "Bring cleaning supplies": 12,
    "Clean inside the oven": 25,
    "Clean inside the fridge": 20,
}

PROFILES = [
    {
        "id": "sofia",
        "name": "Sofia M.",
        "initials": "SM",
        "base": "Luzern",
        "areas": ("Luzern", "Meggen", "Greppen"),
        "services": ("Regular home cleaning", "Deep cleaning"),
        "languages": ("English", "German", "Portuguese"),
        "rating": 4.9,
        "jobs": 126,
        "premium": 0,
        "bio": "Focuses on recurring home visits and detailed kitchen cleans.",
    },
    {
        "id": "lea",
        "name": "Lea K.",
        "initials": "LK",
        "base": "Weggis",
        "areas": ("Weggis", "Vitznau", "Greppen", "Meggen"),
        "services": ("Regular home cleaning", "Deep cleaning", "Move-out cleaning"),
        "languages": ("English", "German", "French"),
        "rating": 4.8,
        "jobs": 94,
        "premium": 4,
        "bio": "Works across the lake communities and specialises in handover cleans.",
    },
    {
        "id": "amina",
        "name": "Amina B.",
        "initials": "AB",
        "base": "Küssnacht am Rigi",
        "areas": ("Küssnacht am Rigi", "Greppen", "Weggis", "Vitznau"),
        "services": ("Regular home cleaning", "Deep cleaning"),
        "languages": ("English", "German", "Arabic"),
        "rating": 4.9,
        "jobs": 74,
        "premium": 2,
        "bio": "Offers recurring visits and one-off deep cleans around Mount Rigi.",
    },
    {
        "id": "daniel",
        "name": "Daniel R.",
        "initials": "DR",
        "base": "Meggen",
        "areas": ("Luzern", "Meggen", "Küssnacht am Rigi"),
        "services": ("Deep cleaning", "Move-out cleaning"),
        "languages": ("English", "German", "Spanish"),
        "rating": 4.8,
        "jobs": 113,
        "premium": 5,
        "bio": "Specialises in larger apartments and end-of-tenancy cleaning.",
    },
    {
        "id": "elif",
        "name": "Elif A.",
        "initials": "EA",
        "base": "Greppen",
        "areas": ("Luzern", "Meggen", "Greppen", "Weggis", "Vitznau", "Küssnacht am Rigi"),
        "services": ("Regular home cleaning", "Deep cleaning", "Move-out cleaning"),
        "languages": ("English", "German", "Turkish"),
        "rating": 4.9,
        "jobs": 82,
        "premium": 3,
        "bio": "Handles regular visits and move-out cleans throughout the service area.",
    },
]

STATUSES = ("Requested", "Confirmed", "On the way", "In progress", "Completed")

st.session_state.setdefault("lc_bookings", [])
st.session_state.setdefault("lc_selected", None)
st.session_state.setdefault("lc_notice", None)


def select_cleaner(profile_id):
    st.session_state.lc_selected = profile_id


def maps_url(kind, **params):
    return f"https://www.google.com/maps/{kind}/?{urlencode({'api': 1, **params})}"


def service_price(profile, service):
    return SERVICES[service][1] + profile["premium"]


def overlapping_booking(profile_id, starts, ends):
    return any(
        booking["profile_id"] == profile_id
        and booking["status"] != "Cancelled"
        and starts < booking["ends"]
        and ends > booking["starts"]
        for booking in st.session_state.lc_bookings
    )


def change_status(booking_id, status):
    for booking in st.session_state.lc_bookings:
        if booking["id"] == booking_id:
            booking["status"] = status
            booking["history"].append((status, datetime.now(ZURICH)))
            return


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Instrument+Serif&display=swap');

    .stApp, [data-testid="stHeader"] { background: #f5f7f3; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1230px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }
    [data-testid="stMainBlockContainer"] :is(h2, h3, h4, p, label) {
        color: #18352b;
        font-family: "DM Sans", sans-serif;
    }
    .lc-hero {
        padding: clamp(32px, 7vw, 82px);
        border-radius: 28px;
        background:
            radial-gradient(ellipse at 92% 2%, #418665, transparent 53%),
            linear-gradient(130deg, #102c23, #1b4d3d);
    }
    .lc-hero h1 {
        margin: 0 0 14px;
        padding: 0;
        color: #fff;
        font: 400 clamp(3.6rem, 8vw, 7rem)/.95 "Instrument Serif", Georgia, serif;
    }
    .lc-hero p {
        color: #e0f1e8 !important;
        margin: 0;
        max-width: 48ch;
    }
    .lc-profile {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .lc-avatar {
        display: grid;
        place-items: center;
        width: 46px;
        height: 46px;
        border-radius: 50%;
        background: #dfefe5;
        color: #194434;
        font: 700 .95rem "DM Sans", sans-serif;
    }
    .lc-profile h4 { margin: 0; padding: 0; }
    .lc-profile small { color: #456655; }
    .lc-quote {
        padding: 24px;
        background: #173d30;
        border-radius: 17px;
        color: #f4fbf6;
    }
    .lc-quote div {
        font: 400 3.7rem/1.15 "Instrument Serif", Georgia, serif;
    }
    .lc-quote p { color: #e1f0e8 !important; margin: 0; }
    button[kind="primary"] {
        background: #205b45;
        border-color: #205b45;
        color: #fff;
    }
    button[kind="primary"]:hover {
        background: #164431;
        border-color: #164431;
        color: #fff;
    }
    </style>
    <div class="lc-hero">
        <h1>Luzern Clean</h1>
        <p>Find a cleaner in the Lucerne area, compare prices, and plan your visit.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Demo · Sample profiles and prices. Bookings are saved for this session.")

find_tab, bookings_tab = st.tabs(
    ["Find a cleaner", f"My bookings ({len(st.session_state.lc_bookings)})"]
)

with find_tab:
    st.subheader("Find a cleaner in your area")
    filter_columns = st.columns(4)

    with filter_columns[0]:
        area = st.selectbox("Service area", list(AREAS))
    with filter_columns[1]:
        service = st.selectbox("Service", list(SERVICES))
    with filter_columns[2]:
        language = st.selectbox(
            "Preferred language",
            ["Any"] + sorted({lang for profile in PROFILES for lang in profile["languages"]}),
        )
    with filter_columns[3]:
        order = st.selectbox("Sort by", ["Top rated", "Lowest hourly rate", "Most jobs"])

    st.caption(SERVICES[service][2])
    matches = [
        profile
        for profile in PROFILES
        if area in profile["areas"]
        and service in profile["services"]
        and (language == "Any" or language in profile["languages"])
    ]

    if order == "Lowest hourly rate":
        matches.sort(key=lambda profile: service_price(profile, service))
    elif order == "Most jobs":
        matches.sort(key=lambda profile: -profile["jobs"])
    else:
        matches.sort(key=lambda profile: (-profile["rating"], -profile["jobs"]))

    selected = next(
        (profile for profile in matches if profile["id"] == st.session_state.lc_selected),
        None,
    )

    profiles_column, map_column = st.columns([1, 1], gap="large")

    with profiles_column:
        st.subheader(f"Matching cleaners ({len(matches)})")
        if not matches:
            st.info("No demo profiles match these filters. Try another language or area.")

        for profile in matches:
            active = selected is not None and selected["id"] == profile["id"]
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="lc-profile">
                        <div class="lc-avatar">{profile['initials']}</div>
                        <div>
                            <h4>{profile['name']}</h4>
                            <small>Based in {profile['base']}</small>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.write(
                    f"⭐ {profile['rating']:.1f} · {profile['jobs']} jobs · "
                    f"**CHF {service_price(profile, service)}/hour**"
                )
                st.caption(" · ".join(profile["languages"]))
                with st.expander(f"About {profile['name']}"):
                    st.write(profile["bio"])
                    st.write("Services · " + ", ".join(profile["services"]))
                    st.write("Coverage · " + ", ".join(profile["areas"]))
                st.button(
                    "Selected" if active else f"Choose {profile['name']}",
                    key=f"profile_{profile['id']}",
                    type="primary" if active else "secondary",
                    disabled=active,
                    width="stretch",
                    on_click=select_cleaner,
                    args=(profile["id"],),
                )

    with map_column:
        st.subheader("Service map")
        areas_on_map = list(dict.fromkeys([area] + [profile["base"] for profile in matches]))
        points = [
            {
                "latitude": AREAS[place][0],
                "longitude": AREAS[place][1],
                "marker": "#187850" if place == area else "#d88438",
            }
            for place in areas_on_map
        ]
        st.map(points, color="marker", size=240, height=400)
        st.caption("Green · Selected service area. Orange · Approximate cleaner bases.")
        st.link_button(
            f"Open {area} in Google Maps",
            maps_url("search", query=f"{area}, Switzerland"),
            width="stretch",
        )
        if selected and selected["base"] != area:
            st.link_button(
                f"Directions from {selected['base']}",
                maps_url(
                    "dir",
                    origin=f"{selected['base']}, Switzerland",
                    destination=f"{area}, Switzerland",
                    travelmode="driving",
                ),
                width="stretch",
            )

    if selected:
        st.divider()
        st.subheader(f"Plan your visit with {selected['name']}")
        visit_column, quote_column = st.columns([3, 2], gap="large")
        minimum = SERVICES[service][0]
        rate = service_price(selected, service)

        with visit_column:
            hours = st.slider(
                "Estimated cleaning hours",
                min_value=minimum,
                max_value=8,
                value=minimum,
                key=f"lc_hours_{service}",
            )
            extras = st.multiselect(
                "Extras",
                list(ADD_ONS),
                format_func=lambda label: f"{label} (+CHF {ADD_ONS[label]})",
            )

        total = hours * rate + sum(ADD_ONS[extra] for extra in extras)

        with quote_column:
            st.markdown(
                f"""
                <div class="lc-quote">
                    <p>Estimated total</p>
                    <div>CHF {total:,.0f}</div>
                    <p>{hours} hours × CHF {rate} plus selected extras</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("Demo estimate. Final scope and price require confirmation.")

        now = datetime.now(ZURICH)
        today = now.date()
        possible_hours = range(8, 20 - hours + 1)

        with st.form("lc_booking"):
            date_column, time_column = st.columns(2)
            with date_column:
                visit_date = st.date_input(
                    "Preferred date",
                    value=today + timedelta(days=1),
                    min_value=today,
                    max_value=today + timedelta(days=90),
                    format="DD.MM.YYYY",
                )
            with time_column:
                start_hour = st.selectbox(
                    "Start time · Swiss local time",
                    list(possible_hours),
                    format_func=lambda hour: f"{hour:02d}:00",
                )

            submitted = st.form_submit_button(
                "Request this cleaner", type="primary", width="stretch"
            )

        if submitted:
            starts = datetime.combine(visit_date, time(start_hour), tzinfo=ZURICH)
            ends = starts + timedelta(hours=hours)

            if starts <= datetime.now(ZURICH):
                st.error("Choose a start time in the future.")
            elif overlapping_booking(selected["id"], starts, ends):
                st.error("This overlaps with one of your existing demo bookings.")
            else:
                booking_id = uuid4().hex[:8].upper()
                st.session_state.lc_bookings.append({
                    "id": booking_id,
                    "profile_id": selected["id"],
                    "cleaner": selected["name"],
                    "service": service,
                    "area": area,
                    "starts": starts,
                    "ends": ends,
                    "total": total,
                    "extras": extras,
                    "status": "Requested",
                    "history": [("Requested", datetime.now(ZURICH))],
                })
                st.session_state.lc_notice = (
                    f"Request {booking_id} saved. See My bookings for its status."
                )
                st.rerun()

    notice = st.session_state.pop("lc_notice", None)
    if notice:
        st.success(notice)


with bookings_tab:
    st.subheader("My bookings")
    if not st.session_state.lc_bookings:
        st.info("Choose a cleaner and request a visit to see your booking here.")

    for booking in reversed(st.session_state.lc_bookings):
        booking_id = booking["id"]
        status = booking["status"]

        with st.container(border=True):
            info_column, price_column = st.columns([3, 1])

            with info_column:
                st.markdown(f"**{booking['service']} with {booking['cleaner']}**")
                st.write(
                    f"{booking['area']} · {booking['starts']:%d.%m.%Y} · "
                    f"{booking['starts']:%H:%M}–{booking['ends']:%H:%M}"
                )
                if booking["extras"]:
                    st.caption("Extras · " + ", ".join(booking["extras"]))

            with price_column:
                st.metric("Estimate", f"CHF {booking['total']:,.0f}")

            st.write(f"**{status}** · Reference `{booking_id}`")
            if status in STATUSES:
                step = STATUSES.index(status)
                st.progress((step + 1) / len(STATUSES))

                if step + 1 < len(STATUSES):
                    next_status = STATUSES[step + 1]
                    st.button(
                        f"Simulate {next_status.lower()}",
                        key=f"lc_progress_{booking_id}",
                        on_click=change_status,
                        args=(booking_id, next_status),
                    )

            if status in ("Requested", "Confirmed"):
                st.button(
                    "Cancel request",
                    key=f"lc_cancel_{booking_id}",
                    on_click=change_status,
                    args=(booking_id, "Cancelled"),
                )

            with st.expander("Status history"):
                for event_status, event_time in booking["history"]:
                    st.write(f"{event_time:%d.%m.%Y %H:%M} · {event_status}")
