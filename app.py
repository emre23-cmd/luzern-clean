from datetime import datetime, time, timedelta
from urllib.parse import urlencode
from uuid import uuid4
from zoneinfo import ZoneInfo

import streamlit as st


st.set_page_config(
    page_title="Luzern Clean",
    page_icon="🌿",
    layout="wide",
)

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
    "Regular home cleaning": (2, 45),
    "Deep cleaning": (3, 55),
    "Move-out cleaning": (4, 60),
}
EXTRAS = {
    "Cleaning supplies": 12,
    "Inside the oven": 25,
    "Inside the fridge": 20,
}
CLEANERS = {
    "sofia": {
        "name": "Sofia M.",
        "initials": "SM",
        "base": "Luzern",
        "areas": ("Luzern", "Meggen", "Greppen"),
        "services": ("Regular home cleaning", "Deep cleaning"),
        "languages": ("English", "German", "Portuguese"),
        "rating": 4.9,
        "jobs": 126,
        "premium": 0,
        "bio": "Sofia focuses on recurring home visits and detailed kitchen cleans.",
    },
    "lea": {
        "name": "Lea K.",
        "initials": "LK",
        "base": "Weggis",
        "areas": ("Weggis", "Vitznau", "Greppen", "Meggen"),
        "services": tuple(SERVICES),
        "languages": ("English", "German", "French"),
        "rating": 4.8,
        "jobs": 94,
        "premium": 4,
        "bio": "Lea covers the lakeside communities and specialises in move-out cleans.",
    },
    "amina": {
        "name": "Amina B.",
        "initials": "AB",
        "base": "Küssnacht am Rigi",
        "areas": ("Küssnacht am Rigi", "Greppen", "Weggis", "Vitznau"),
        "services": ("Regular home cleaning", "Deep cleaning"),
        "languages": ("English", "German", "Arabic"),
        "rating": 4.9,
        "jobs": 74,
        "premium": 2,
        "bio": "Amina offers regular visits and one-off deep cleans around Mount Rigi.",
    },
    "daniel": {
        "name": "Daniel R.",
        "initials": "DR",
        "base": "Meggen",
        "areas": ("Luzern", "Meggen", "Küssnacht am Rigi"),
        "services": ("Deep cleaning", "Move-out cleaning"),
        "languages": ("English", "German", "Spanish"),
        "rating": 4.8,
        "jobs": 113,
        "premium": 5,
        "bio": "Daniel specialises in larger apartments and end-of-tenancy cleaning.",
    },
    "elif": {
        "name": "Elif A.",
        "initials": "EA",
        "base": "Greppen",
        "areas": tuple(AREAS),
        "services": tuple(SERVICES),
        "languages": ("English", "German", "Turkish"),
        "rating": 4.9,
        "jobs": 82,
        "premium": 3,
        "bio": "Elif handles regular visits and move-out cleans throughout the service area.",
    },
}
STATUS_FLOW = ("Requested", "Confirmed", "On the way", "In progress", "Completed")
DEMO_CARDS = {"Visa": "4242", "Mastercard": "4444"}

state = st.session_state
state.setdefault("lc_orders", [])
state.setdefault("lc_personal", {"name": "", "email": "", "phone": ""})
state.setdefault("lc_preferences", {"language": "English", "reminders": True})
state.setdefault("lc_addresses", {})
state.setdefault("lc_cards", {})


def swiss_now():
    return datetime.now(ZURICH)


def maps_url(kind, **params):
    query = urlencode({"api": 1, **params})
    return f"https://www.google.com/maps/{kind}/?{query}"


def hourly_rate(cleaner, service):
    return SERVICES[service][1] + cleaner["premium"]


def visit_label(order):
    return f"{order['starts']:%d.%m.%Y · %H:%M}–{order['ends']:%H:%M}"


def back(label, page):
    if st.button(label, key=f"back_{page.url_path}"):
        st.switch_page(page)


def cleaner_header(cleaner):
    # HTML values come only from the fixed demo profile catalogue.
    st.markdown(
        f"""
        <div class="lc-person">
            <span class="lc-avatar">{cleaner['initials']}</span>
            <div><strong>{cleaner['name']}</strong>
            <small>Based in {cleaner['base']}</small></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_map(area, cleaners):
    places = list(dict.fromkeys([area, *(cleaner["base"] for cleaner in cleaners)]))
    st.map(
        {
            "lat": [AREAS[place][0] for place in places],
            "lon": [AREAS[place][1] for place in places],
            "color": ["#157049" if place == area else "#D0793A" for place in places],
        },
        latitude="lat",
        longitude="lon",
        color="color",
        size=210,
        height=390,
    )
    st.caption("Green pin · Your service area. Orange pins · Cleaner base towns.")
    st.link_button(
        f"Open {area} in Google Maps",
        maps_url("search", query=f"{area}, Switzerland"),
        width="stretch",
    )


def explore():
    st.markdown(
        """
        <div class="lc-hero">
            <h1>Where do you need cleaning?</h1>
            <p>Find a cleaner, compare rates and choose a time that works for you.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    a, b, c, d = st.columns(4)
    with a:
        area = st.selectbox("Visit area", list(AREAS))
    with b:
        service = st.selectbox("Service", list(SERVICES))
    with c:
        languages = sorted({lang for person in CLEANERS.values() for lang in person["languages"]})
        language = st.selectbox("Cleaner language", ["Any", *languages])
    with d:
        sort = st.selectbox("Sort by", ["Top rated", "Lowest price", "Most jobs"])

    matches = [
        (key, person)
        for key, person in CLEANERS.items()
        if area in person["areas"]
        and service in person["services"]
        and (language == "Any" or language in person["languages"])
    ]
    order_by = {
        "Top rated": lambda item: (-item[1]["rating"], -item[1]["jobs"]),
        "Lowest price": lambda item: hourly_rate(item[1], service),
        "Most jobs": lambda item: -item[1]["jobs"],
    }
    matches.sort(key=order_by[sort])

    view = st.segmented_control(
        "Results view", ["Split", "List", "Map"], default="Split"
    ) or "Split"
    if view == "Split":
        list_column, map_column = st.columns([1, 1], gap="large")
    else:
        list_column = map_column = st.container()

    if view != "Map":
        with list_column:
            st.subheader(f"Matching cleaners ({len(matches)})")
            if not matches:
                st.info("Try another service, area or cleaner language.")
            for key, cleaner in matches:
                with st.container(border=True):
                    cleaner_header(cleaner)
                    st.write(
                        f"★ {cleaner['rating']:.1f} · {cleaner['jobs']} jobs · "
                        f"**CHF {hourly_rate(cleaner, service)}/h**"
                    )
                    st.caption(" · ".join(cleaner["languages"]))
                    if st.button("View profile", key=f"profile_{key}", width="stretch"):
                        state.lc_choice = {"cleaner": key, "area": area, "service": service}
                        st.switch_page(PROFILE_PAGE)

    if view != "List":
        with map_column:
            st.subheader("Service map")
            show_map(area, [cleaner for _, cleaner in matches])


def profile():
    back("← Explore", EXPLORE_PAGE)
    choice = state.get("lc_choice")
    if not choice:
        st.info("Choose a cleaner in Explore to view their profile.")
        return

    cleaner = CLEANERS[choice["cleaner"]]
    area, service = choice["area"], choice["service"]
    info, action = st.columns([3, 2], gap="large")

    with info:
        with st.container(border=True):
            cleaner_header(cleaner)
            st.write(f"**★ {cleaner['rating']:.1f}** · {cleaner['jobs']} completed demo jobs")
            st.write(cleaner["bio"])
            st.write("**Languages** · " + ", ".join(cleaner["languages"]))
            st.write("**Services** · " + ", ".join(cleaner["services"]))
            st.write("**Coverage** · " + ", ".join(cleaner["areas"]))

    with action:
        with st.container(border=True):
            st.subheader(service)
            st.write(f"Visit area · {area}")
            st.metric("Hourly rate", f"CHF {hourly_rate(cleaner, service)}")
            if st.button("Choose date and extras", type="primary", width="stretch"):
                st.switch_page(CHECKOUT_PAGE)
            st.link_button(
                "Open route in Google Maps",
                maps_url(
                    "dir",
                    origin=f"{cleaner['base']}, Switzerland",
                    destination=f"{area}, Switzerland",
                    travelmode="driving",
                ),
                width="stretch",
            )


def checkout():
    back("← Cleaner profile", PROFILE_PAGE)
    choice = state.get("lc_choice")
    if not choice:
        st.info("Choose a cleaner in Explore first.")
        return

    cleaner = CLEANERS[choice["cleaner"]]
    service, area = choice["service"], choice["area"]
    minimum = SERVICES[service][0]
    rate = hourly_rate(cleaner, service)
    today = swiss_now().date()

    st.title("Review your visit")
    st.write(f"{service} with **{cleaner['name']}** in {area}")
    form_column, price_column = st.columns([3, 2], gap="large")

    with form_column:
        st.subheader("Date and extras")
        hours = st.slider("Estimated hours", minimum, 8, minimum, key=f"hours_{service}")
        extras = st.multiselect(
            "Add extras",
            list(EXTRAS),
            format_func=lambda name: f"{name} (+CHF {EXTRAS[name]})",
        )
        day_col, hour_col = st.columns(2)
        with day_col:
            day = st.date_input(
                "Visit date",
                value=today + timedelta(days=1),
                min_value=today,
                max_value=today + timedelta(days=90),
                format="DD.MM.YYYY",
            )

        available = []
        for hour in range(8, 20 - hours + 1):
            starts = datetime.combine(day, time(hour), tzinfo=ZURICH)
            ends = starts + timedelta(hours=hours)
            occupied = any(
                order["cleaner"] == choice["cleaner"]
                and order["status"] in STATUS_FLOW[:-1]
                and starts < order["ends"]
                and ends > order["starts"]
                for order in state.lc_orders
            )
            if starts > swiss_now() and not occupied:
                available.append(starts)

        with hour_col:
            starts = st.selectbox(
                "Start time · Swiss local time",
                available,
                format_func=lambda slot: slot.strftime("%H:%M"),
                placeholder="No times available",
            )

        st.subheader("Address and payment")
        address_options = {
            key: address["label"]
            for key, address in state.lc_addresses.items()
            if address["area"] == area
        }
        address = st.selectbox(
            "Visit address",
            [None, *address_options],
            format_func=lambda key: address_options[key] if key else f"Use {area} only",
        )
        card = st.selectbox(
            "Payment method",
            [None, *state.lc_cards],
            format_func=lambda key: state.lc_cards[key] if key else "Pay after service · demo",
        )
        st.page_link(ACCOUNT_PAGE, label="Manage addresses and payment methods")

    subtotal = hours * rate
    total = subtotal + sum(EXTRAS[name] for name in extras)
    with price_column:
        with st.container(border=True):
            st.subheader("Price breakdown")
            st.write(f"{hours} hours × CHF {rate}  ·  CHF {subtotal}")
            for name in extras:
                st.write(f"{name}  ·  CHF {EXTRAS[name]}")
            st.divider()
            st.metric("Estimated total", f"CHF {total}")
            submitted = st.button(
                "Request booking",
                type="primary",
                width="stretch",
                disabled=starts is None,
            )
            st.caption("Demo booking. No charge will be made.")

    if submitted and starts is not None:
        if starts <= swiss_now():
            st.error("This start time has passed. Choose a later time.")
            return
        booking = {
            **choice,
            "id": uuid4().hex[:8].upper(),
            "starts": starts,
            "ends": starts + timedelta(hours=hours),
            "total": total,
            "extras": extras,
            "address": address_options.get(address, area),
            "payment": state.lc_cards.get(card, "Pay after service · demo"),
            "status": "Requested",
            "history": [("Requested", swiss_now())],
        }
        state.lc_orders.append(booking)
        state.lc_order_id = booking["id"]
        st.switch_page(DETAIL_PAGE)


def bookings():
    st.title("Bookings")
    completed = [order for order in state.lc_orders if order["status"] == "Completed"]
    a, b, c = st.columns(3)
    a.metric("Total requests", len(state.lc_orders))
    b.metric("Completed services", len(completed))
    c.metric("Total spent · demo", f"CHF {sum(item['total'] for item in completed)}")

    group = st.segmented_control(
        "Booking history",
        ["Upcoming", "Past services", "Cancelled"],
        default="Upcoming",
    ) or "Upcoming"
    groups = {
        "Upcoming": STATUS_FLOW[:-1],
        "Past services": ("Completed",),
        "Cancelled": ("Cancelled",),
    }
    matching = [order for order in state.lc_orders if order["status"] in groups[group]]

    if not matching:
        st.info("No bookings in this section yet.")
        st.page_link(EXPLORE_PAGE, label="Find a cleaner")

    for order in sorted(matching, key=lambda item: item["starts"], reverse=group != "Upcoming"):
        with st.container(border=True):
            left, right = st.columns([3, 1])
            with left:
                st.markdown(f"**{order['service']} · {CLEANERS[order['cleaner']]['name']}**")
                st.write(f"{order['area']} · {visit_label(order)}")
                st.caption(f"{order['status']} · {order['id']}")
            with right:
                st.write(f"**CHF {order['total']}**")
                if st.button("View details", key=f"view_{order['id']}", width="stretch"):
                    state.lc_order_id = order["id"]
                    st.switch_page(DETAIL_PAGE)


def booking_detail():
    back("← Bookings", BOOKINGS_PAGE)
    order = next(
        (item for item in state.lc_orders if item["id"] == state.get("lc_order_id")),
        None,
    )
    if order is None:
        st.info("Open a reservation from Bookings to see its details.")
        return

    st.title(order["service"])
    st.write(f"With **{CLEANERS[order['cleaner']]['name']}** · {visit_label(order)}")
    details, activity = st.columns(2, gap="large")
    with details:
        with st.container(border=True):
            st.subheader("Visit details")
            st.text(f"{order['address']} · {order['area']}")
            st.write(f"**CHF {order['total']}** · {order['payment']}")
            if order["extras"]:
                st.caption("Extras · " + ", ".join(order["extras"]))
            st.caption(f"Booking reference · {order['id']}")

    with activity:
        with st.container(border=True):
            status = order["status"]
            st.subheader(status)
            if status in STATUS_FLOW:
                step = STATUS_FLOW.index(status)
                st.progress((step + 1) / len(STATUS_FLOW))
                if step < len(STATUS_FLOW) - 1:
                    next_status = STATUS_FLOW[step + 1]
                    if st.button(f"Demo · mark as {next_status.lower()}"):
                        order["status"] = next_status
                        order["history"].append((next_status, swiss_now()))
                        st.rerun()

            if status in ("Requested", "Confirmed"):
                if st.button("Cancel booking"):
                    order["status"] = "Cancelled"
                    order["history"].append(("Cancelled", swiss_now()))
                    st.rerun()

            if status in ("Completed", "Cancelled"):
                if st.button("Book again", type="primary"):
                    state.lc_choice = {key: order[key] for key in ("cleaner", "area", "service")}
                    st.switch_page(CHECKOUT_PAGE)

            with st.expander("Status history"):
                for event, timestamp in reversed(order["history"]):
                    st.write(f"**{event}** · {timestamp:%d.%m.%Y %H:%M}")


def account():
    st.title("Account")
    if state.lc_personal["name"]:
        st.text(state.lc_personal["name"])

    items = [
        ("Personal info", "Name, email and phone", PERSONAL_PAGE),
        ("Saved addresses", f"{len(state.lc_addresses)} saved", ADDRESSES_PAGE),
        ("Payment methods", f"{len(state.lc_cards)} demo cards", PAYMENTS_PAGE),
        ("Account settings", "Language preference and reminders", SETTINGS_PAGE),
    ]
    for label, description, page in items:
        with st.container(border=True):
            st.page_link(page, label=label)
            st.caption(description)


def personal():
    back("← Account", ACCOUNT_PAGE)
    st.title("Personal info")
    st.caption("Use sample details in this demo.")
    current = state.lc_personal
    with st.form("personal_form"):
        name = st.text_input("Full name", value=current["name"], max_chars=80)
        email = st.text_input("Email", value=current["email"], max_chars=120)
        phone = st.text_input("Phone", value=current["phone"], max_chars=30)
        if st.form_submit_button("Save changes", type="primary"):
            if email and ("@" not in email or " " in email):
                st.error("Enter an email address such as name@example.com.")
            else:
                state.lc_personal = {
                    "name": name.strip(), "email": email.strip(), "phone": phone.strip()
                }
                st.success("Personal info saved for this session.")


def addresses():
    back("← Account", ACCOUNT_PAGE)
    st.title("Saved addresses")
    st.caption("Use a label such as Home or Office. Street addresses are unnecessary in this demo.")

    for key, item in list(state.lc_addresses.items()):
        with st.container(border=True):
            st.text(f"{item['label']} · {item['area']}")
            if st.button("Remove", key=f"remove_address_{key}"):
                del state.lc_addresses[key]
                st.rerun()

    with st.form("address_form", clear_on_submit=True):
        label = st.text_input("Address label", max_chars=50)
        area = st.selectbox("Municipality", list(AREAS))
        if st.form_submit_button("Add address", type="primary"):
            if not label.strip():
                st.error("Enter a label for this address.")
            else:
                state.lc_addresses[uuid4().hex] = {"label": label.strip(), "area": area}
                st.rerun()


def payments():
    back("← Account", ACCOUNT_PAGE)
    st.title("Payment methods")
    st.caption("Sample cards only. The app never asks for card numbers or security codes.")

    for brand, label in list(state.lc_cards.items()):
        with st.container(border=True):
            st.write(label)
            if st.button("Remove", key=f"remove_card_{brand}"):
                del state.lc_cards[brand]
                st.rerun()

    available = [brand for brand in DEMO_CARDS if brand not in state.lc_cards]
    if available:
        with st.form("payment_form"):
            brand = st.selectbox("Demo card", available)
            if st.form_submit_button("Add payment method", type="primary"):
                state.lc_cards[brand] = f"{brand} ···· {DEMO_CARDS[brand]}"
                st.rerun()


def settings():
    back("← Account", ACCOUNT_PAGE)
    st.title("Account settings")
    st.caption("These preferences are saved for the demo session. The interface is in English.")
    languages = ["English", "Deutsch", "Türkçe"]
    with st.form("settings_form"):
        language = st.selectbox(
            "Preferred language",
            languages,
            index=languages.index(state.lc_preferences["language"]),
        )
        reminders = st.toggle(
            "Booking reminders", value=state.lc_preferences["reminders"]
        )
        if st.form_submit_button("Save settings", type="primary"):
            state.lc_preferences = {"language": language, "reminders": reminders}
            st.success("Preferences saved for this session.")


EXPLORE_PAGE = st.Page(explore, title="Explore", icon=":material/explore:", default=True)
BOOKINGS_PAGE = st.Page(bookings, title="Bookings", icon=":material/calendar_month:", url_path="bookings")
ACCOUNT_PAGE = st.Page(account, title="Account", icon=":material/person:", url_path="account")
PROFILE_PAGE = st.Page(profile, title="Cleaner profile", url_path="cleaner")
CHECKOUT_PAGE = st.Page(checkout, title="Review visit", url_path="review")
DETAIL_PAGE = st.Page(booking_detail, title="Booking details", url_path="booking")
PERSONAL_PAGE = st.Page(personal, title="Personal info", url_path="personal-info")
ADDRESSES_PAGE = st.Page(addresses, title="Saved addresses", url_path="addresses")
PAYMENTS_PAGE = st.Page(payments, title="Payment methods", url_path="payments")
SETTINGS_PAGE = st.Page(settings, title="Account settings", url_path="settings")

page = st.navigation(
    [
        EXPLORE_PAGE, BOOKINGS_PAGE, ACCOUNT_PAGE, PROFILE_PAGE, CHECKOUT_PAGE,
        DETAIL_PAGE, PERSONAL_PAGE, ADDRESSES_PAGE, PAYMENTS_PAGE, SETTINGS_PAGE,
    ],
    position="hidden",
)

st.html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Instrument+Serif&display=swap');
    :root { --lc-green: #1c6248; --lc-ink: #18362d; }
    .stApp { background: #f6f8f3; }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1200px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        color: var(--lc-ink);
        font-family: "DM Sans", sans-serif;
    }
    [data-testid="stMainBlockContainer"] :is(h1,h2,h3,p,label) {
        color: var(--lc-ink);
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(> div > .lc-person) {
        background: white;
    }
    .lc-brand { font: 700 1.2rem "DM Sans", sans-serif; color: var(--lc-ink); }
    .lc-hero {
        background: radial-gradient(ellipse at 94% 0%, #4a896a, transparent 59%),
                    linear-gradient(125deg, #15392c, #1d5943);
        padding: clamp(28px, 6vw, 68px);
        border-radius: 26px;
        margin-bottom: 8px;
    }
    .lc-hero h1 {
        color: white !important;
        font: 400 clamp(2.7rem, 6vw, 5rem)/1 "Instrument Serif", Georgia, serif;
        margin: 0;
        padding: 0;
    }
    .lc-hero p { color: #e0f1e7 !important; margin: 14px 0 0; }
    .lc-person { display: flex; align-items: center; gap: 14px; }
    .lc-person strong { color: var(--lc-ink); font-size: 1.1rem; }
    .lc-person small { display: block; color: #4d695c; }
    .lc-avatar {
        width: 50px;
        height: 50px;
        display: grid;
        place-items: center;
        border-radius: 16px;
        background: #dcf0e4;
        color: #1a5a40;
        font-weight: 700;
    }
    button[kind="primary"] {
        background: var(--lc-green);
        border-color: var(--lc-green);
        color: white;
    }
    </style>
    """
)

st.html('<div class="lc-brand">Luzern Clean</div>')
nav_columns = st.columns(3)
for col, destination in zip(nav_columns, (EXPLORE_PAGE, BOOKINGS_PAGE, ACCOUNT_PAGE)):
    with col:
        st.page_link(destination, width="stretch")

st.divider()
page.run()
st.divider()
st.caption("Luzern Clean demo · Sample cleaners and prices · Session-only data")
