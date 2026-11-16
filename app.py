from datetime import datetime, time, timedelta, timezone
from html import escape
from urllib.parse import urlencode
from uuid import uuid4
from zoneinfo import ZoneInfo

import streamlit as st


st.set_page_config(page_title="Luzern Clean", page_icon="🌿", layout="wide")

SWISS_TIME = ZoneInfo("Europe/Zurich")

AREAS = {
    "Luzern": (47.0502, 8.3093),
    "Meggen": (47.0465, 8.3740),
    "Greppen": (47.0561, 8.4299),
    "Weggis": (47.0321, 8.4337),
    "Vitznau": (47.0106, 8.4839),
    "Küssnacht am Rigi": (47.0830, 8.4410),
}

REGULAR = "Regular home cleaning"
DEEP = "Deep cleaning"
MOVE_OUT = "Move-out cleaning"

SERVICES = {
    REGULAR: (2, 45, "Routine cleaning for kitchens, bathrooms, floors and surfaces."),
    DEEP: (3, 55, "Extra attention to buildup and hard-to-reach areas."),
    MOVE_OUT: (4, 60, "A thorough clean for an empty home before handover."),
}

EXTRAS = {
    "Bring cleaning supplies": 12,
    "Clean inside the oven": 25,
    "Clean inside the fridge": 20,
}

WEEKDAYS = (0, 1, 2, 3, 4)
MON_SAT = (*WEEKDAYS, 5)
EVERY_DAY = (*MON_SAT, 6)
DAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
BOTH_PETS = ("Dogs", "Cats")
STATUSES = ("Requested", "Confirmed", "On the way", "In progress", "Completed")
ACTIVE = STATUSES[:-1]
DEMO_CARDS = {"Visa": "4242", "Mastercard": "4444"}

TEAM = [
    ("Emre", "Chief Executive Officer", "Company direction, strategy and business development."),
    ("Joel", "Head of Operations", "Service delivery, scheduling and cleaner onboarding."),
    ("Salma", "Head of Customer Experience", "Customer support, service feedback and issue resolution."),
    ("Akin", "Head of IT & Infrastructure", "Platform development, infrastructure and reliability."),
    ("Tapesh", "Head of Partnerships & Growth", "Local partnerships, cleaner network growth and expansion."),
]


def cleaner(name, base, areas, services, languages, rating, jobs, premium, pets,
            days, hours, offer, bio):
    return {
        "name": name, "base": base, "areas": areas, "services": services,
        "languages": languages, "rating": rating, "jobs": jobs, "premium": premium,
        "pets": pets, "days": days, "hours": hours, "offer": offer, "bio": bio,
    }


# Offers are (discount %, earliest start hour, latest start hour).
CLEANERS = {
    "sofia": cleaner(
        "Sofia M.", "Luzern", ("Luzern", "Meggen", "Greppen"), (REGULAR, DEEP),
        ("English", "German", "Portuguese"), 4.9, 126, 0, BOTH_PETS,
        WEEKDAYS, (8, 18), (15, 11, 14),
        "Focuses on recurring home visits and detailed kitchen cleans.",
    ),
    "lea": cleaner(
        "Lea K.", "Weggis", ("Weggis", "Vitznau", "Greppen", "Meggen"), tuple(SERVICES),
        ("English", "German", "French"), 4.8, 94, 4, ("Cats",),
        MON_SAT, (8, 18), None,
        "Specialises in handover cleans around the lakeside communities.",
    ),
    "amina": cleaner(
        "Amina B.", "Küssnacht am Rigi", ("Küssnacht am Rigi", "Greppen", "Weggis", "Vitznau"),
        (REGULAR, DEEP), ("English", "German", "Arabic"), 4.9, 74, 2, BOTH_PETS,
        MON_SAT, (9, 18), (10, 13, 15),
        "Offers recurring visits and one-off deep cleans around Mount Rigi.",
    ),
    "daniel": cleaner(
        "Daniel R.", "Meggen", ("Luzern", "Meggen", "Küssnacht am Rigi"), (DEEP, MOVE_OUT),
        ("English", "German", "Spanish"), 4.8, 113, 5, ("Dogs",),
        WEEKDAYS, (8, 19), None,
        "Works on larger apartments and end-of-tenancy cleaning.",
    ),
    "elif": cleaner(
        "Elif A.", "Greppen", tuple(AREAS), tuple(SERVICES),
        ("English", "German", "Turkish"), 4.9, 82, 3, BOTH_PETS,
        MON_SAT, (8, 19), (10, 10, 12),
        "Handles regular visits and move-out cleans throughout the service area.",
    ),
    "maya": cleaner(
        "Maya L.", "Luzern", ("Luzern", "Meggen", "Küssnacht am Rigi"), (REGULAR, DEEP),
        ("English", "German", "Italian"), 4.9, 68, 1, BOTH_PETS,
        (1, 2, 3, 4, 5), (8, 18), (20, 9, 11),
        "Offers morning appointments and has experience in homes with pets.",
    ),
    "jonas": cleaner(
        "Jonas F.", "Küssnacht am Rigi", ("Küssnacht am Rigi", "Greppen", "Weggis", "Meggen"),
        tuple(SERVICES), ("English", "German"), 4.7, 57, -2, ("Dogs",),
        MON_SAT, (9, 19), (15, 13, 15),
        "Focuses on weekly cleaning and flexible afternoon visits.",
    ),
    "nina": cleaner(
        "Nina P.", "Vitznau", ("Vitznau", "Weggis", "Greppen"), (REGULAR, DEEP),
        ("English", "German", "French"), 4.8, 61, 2, ("Cats",),
        (3, 4, 5, 6), (9, 18), None,
        "Offers weekend bookings and detailed cleaning for smaller homes.",
    ),
    "samir": cleaner(
        "Samir H.", "Luzern", ("Luzern", "Meggen", "Greppen"), tuple(SERVICES),
        ("English", "German", "Arabic"), 4.9, 91, 4, BOTH_PETS,
        EVERY_DAY, (10, 20), (15, 15, 17),
        "Offers later appointments, deep cleans and apartment handovers.",
    ),
}

state = st.session_state
state.setdefault("lc_orders", [])
state.setdefault("lc_favourites", set())
state.setdefault("lc_personal", {"name": "", "email": "", "phone": ""})
state.setdefault("lc_addresses", {})
state.setdefault("lc_cards", {})
state.setdefault("lc_preferences", {"language": "English", "reminders": True})
state.setdefault("lc_applications", [])
state.setdefault("lc_filter", {})
state.setdefault("lc_checkout_version", 0)


def now():
    return datetime.now(SWISS_TIME)


def money(cents):
    return f"CHF {cents / 100:,.2f}"


def maps_url(action, **params):
    return f"https://www.google.com/maps/{action}/?{urlencode({'api': 1, **params})}"


def rate(person, service):
    return SERVICES[service][1] + person["premium"]


def discount_for(person, slot):
    offer = person["offer"]
    if slot is not None and offer and offer[1] <= slot.hour <= offer[2]:
        return offer[0]
    return 0


def order_total(order):
    if "total_cents" in order:
        return order["total_cents"]
    return round(order["total"] * 100)


def visit_label(order):
    return f"{order['starts']:%d.%m.%Y · %H:%M}–{order['ends']:%H:%M}"


def pet_label(person):
    return "Dogs & cats welcome" if person["pets"] == BOTH_PETS else f"{person['pets'][0]} welcome"


def slots_for(cleaner_id, day, hours):
    person = CLEANERS[cleaner_id]
    if day.weekday() not in person["days"]:
        return []

    opens, closes = person["hours"]
    current = now()
    booked = [
        order for order in state.lc_orders
        if order["cleaner"] == cleaner_id and order["status"] in ACTIVE
    ]
    slots = []
    for hour in range(opens, closes - hours + 1):
        starts = datetime.combine(day, time(hour), tzinfo=SWISS_TIME)
        ends = starts + timedelta(hours=hours)
        if starts > current and not any(
            starts < order["ends"] and ends > order["starts"] for order in booked
        ):
            slots.append(starts)
    return slots


def next_openings(cleaner_id, service):
    today = now().date()
    hours = SERVICES[service][0]
    slots = [
        slot for offset in range(7)
        for slot in slots_for(cleaner_id, today + timedelta(days=offset), hours)
    ]
    person = CLEANERS[cleaner_id]
    offer_slot = next((slot for slot in slots if discount_for(person, slot)), None)
    return (slots[0] if slots else None), offer_slot


def start_checkout(preferred_slot=None):
    state.lc_preferred_slot = preferred_slot
    state.lc_checkout_version += 1
    st.switch_page(CHECKOUT_PAGE)


def toggle_favourite(cleaner_id):
    if cleaner_id in state.lc_favourites:
        state.lc_favourites.remove(cleaner_id)
    else:
        state.lc_favourites.add(cleaner_id)


def set_status(order, status):
    order["status"] = status
    order["history"].append((status, now()))


def calendar_file(order):
    def stamp(value):
        return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    return "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0",
        "PRODID:-//Luzern Clean//Demo Bookings//EN",
        "BEGIN:VEVENT",
        f"UID:{order['id']}@luzern-clean.demo",
        f"DTSTAMP:{stamp(order['history'][0][1])}",
        f"DTSTART:{stamp(order['starts'])}",
        f"DTEND:{stamp(order['ends'])}",
        "SUMMARY:Luzern Clean demo visit",
        f"LOCATION:{order['area']}",
        "END:VEVENT", "END:VCALENDAR", "",
    ])


def hero(title, description):
    st.html(
        f'<section class="lc-hero"><h1>{escape(title)}</h1>'
        f'<p>{escape(description)}</p></section>'
    )


def identity(name, subtitle):
    initials = "".join(part[0] for part in name.split())[:2]
    st.html(
        f'<div class="lc-identity"><span>{escape(initials)}</span>'
        f'<div><strong>{escape(name)}</strong><small>{escape(subtitle)}</small></div></div>'
    )


def back(destination):
    st.page_link(destination, label=f"← {destination.title}")


def explore():
    hero("Where do you need cleaning?", "Find a local cleaner, compare rates and choose a time.")

    previous = state.lc_filter
    languages = ["Any", *sorted({lang for person in CLEANERS.values() for lang in person["languages"]})]
    pet_options = ["Any", "Dogs", "Cats", "Dogs & cats"]
    sort_options = ["Smart match", "Lowest hourly rate", "Soonest opening", "Top rated"]

    def select(label, options, name):
        options = list(options)
        saved = previous.get(name)
        index = options.index(saved) if saved in options else 0
        return st.selectbox(label, options, index=index, key=f"explore_{name}")

    address_options = {key: item for key, item in state.lc_addresses.items()}
    if address_options:
        saved_address = st.selectbox(
            "Use a saved address",
            [None, *address_options],
            format_func=lambda key: (
                f"{address_options[key]['label']} · {address_options[key]['area']}"
                if key else "Choose an area manually"
            ),
        )
    else:
        saved_address = None

    a, b, c, d = st.columns(4)
    with a:
        if saved_address:
            area = address_options[saved_address]["area"]
            st.text(f"Visit area · {area}")
        else:
            area = select("Visit area", AREAS, "area")
    with b:
        service = select("Service", SERVICES, "service")
    with c:
        pets = select("Pets at home", pet_options, "pets")
    with d:
        language = select("Cleaner language", languages, "language")

    st.caption(SERVICES[service][2])

    a, b, c, d = st.columns([2, 1, 1, 1])
    with a:
        sort = select("Sort by", sort_options, "sort")
    with b:
        offers_only = st.toggle("Discount slots", value=previous.get("offers_only", False))
    with c:
        favourites_only = st.toggle("Favourites", value=previous.get("favourites_only", False))
    with d:
        st.page_link(MAP_PAGE, label="Service Map", icon=":material/map:")

    state.lc_filter = {
        "area": area, "service": service, "pets": pets, "language": language,
        "sort": sort, "offers_only": offers_only, "favourites_only": favourites_only,
    }

    required_pets = {
        "Any": set(), "Dogs": {"Dogs"}, "Cats": {"Cats"}, "Dogs & cats": set(BOTH_PETS),
    }[pets]
    results = []
    for key, person in CLEANERS.items():
        if (
            area not in person["areas"] or service not in person["services"]
            or (language != "Any" and language not in person["languages"])
            or not required_pets.issubset(person["pets"])
            or (favourites_only and key not in state.lc_favourites)
        ):
            continue
        first, offer = next_openings(key, service)
        if not offers_only or offer:
            results.append((key, person, first, offer))

    last = datetime.max.replace(tzinfo=SWISS_TIME)
    rankings = {
        "Smart match": lambda row: (
            row[2] is None, row[3] is None, -row[1]["rating"], -row[1]["jobs"]
        ),
        "Lowest hourly rate": lambda row: rate(row[1], service),
        "Soonest opening": lambda row: row[2] or last,
        "Top rated": lambda row: (-row[1]["rating"], -row[1]["jobs"]),
    }
    results.sort(key=rankings[sort])

    st.subheader(f"{len(results)} matching cleaners")
    if not results:
        st.info("Try another municipality, service or filter.")
        return

    for offset in range(0, len(results), 3):
        columns = st.columns(3)
        for column, (key, person, first, offer) in zip(columns, results[offset:offset + 3]):
            with column, st.container(border=True):
                identity(person["name"], person["base"])
                st.write(f"**★ {person['rating']:.1f}** · {person['jobs']} demo jobs")
                st.write(f"**CHF {rate(person, service)}/hr**")
                st.caption(f"{pet_label(person)} · " + ", ".join(person["languages"]))
                if first:
                    st.caption(f"Next opening · {first:%a %d.%m at %H:%M}")
                if offer:
                    st.html(
                        f'<span class="lc-offer">Save {discount_for(person, offer)}% '
                        f'· {offer:%a %d.%m at %H:%M}</span>'
                    )
                if st.button("View profile", key=f"profile_{key}", width="stretch"):
                    state.lc_choice = {"cleaner": key, "area": area, "service": service}
                    state.lc_preferred_slot = offer if offers_only else first
                    state.lc_preferred_address = saved_address
                    st.switch_page(PROFILE_PAGE)
                st.button(
                    "♥ Saved" if key in state.lc_favourites else "♡ Save",
                    key=f"save_{key}", on_click=toggle_favourite, args=(key,),
                )


def service_map():
    hero("Service Map", "Explore service coverage around Lucerne and the Rigi lakeside.")
    areas = list(AREAS)
    selected = state.lc_filter.get("area", areas[0])
    left, right = st.columns([1, 2], gap="large")

    with left:
        area = st.selectbox("Municipality", areas, index=areas.index(selected), key="map_area")
        service = st.selectbox("Service", list(SERVICES), key="map_service")
        matches = [
            (key, person) for key, person in CLEANERS.items()
            if area in person["areas"] and service in person["services"]
        ]
        st.metric("Matching demo cleaners", len(matches))
        st.link_button(
            "Open area in Google Maps",
            maps_url("search", query=f"{area}, Switzerland"),
            width="stretch",
        )
        for key, person in matches:
            with st.container(border=True):
                identity(person["name"], f"Based in {person['base']}")
                if st.button("View profile", key=f"map_profile_{key}"):
                    state.lc_choice = {"cleaner": key, "area": area, "service": service}
                    state.lc_preferred_slot = None
                    state.lc_preferred_address = None
                    st.switch_page(PROFILE_PAGE)

    with right:
        places = list(dict.fromkeys([area, *(person["base"] for _, person in matches)]))
        st.map(
            {
                "latitude": [AREAS[place][0] for place in places],
                "longitude": [AREAS[place][1] for place in places],
                "pin": ["#1b6247" if place == area else "#d07c44" for place in places],
            },
            latitude="latitude", longitude="longitude", color="pin", size=240, height=480,
        )
        st.caption("Green · Selected municipality. Orange · Approximate cleaner base towns.")


def profile():
    back(EXPLORE_PAGE)
    choice = state.get("lc_choice")
    if not choice:
        st.info("Choose a cleaner from Explore or Service Map.")
        return

    key, area, service = choice["cleaner"], choice["area"], choice["service"]
    person = CLEANERS[key]
    first, offer = next_openings(key, service)
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.title(person["name"])
        st.write(f"**★ {person['rating']:.1f}** · {person['jobs']} demo jobs · Based in {person['base']}")
        st.write(person["bio"])
        st.write(f"**Pet policy** · {pet_label(person)}")
        st.write("**Languages** · " + ", ".join(person["languages"]))
        st.write("**Services** · " + ", ".join(person["services"]))
        st.write("**Coverage** · " + ", ".join(person["areas"]))
        opens, closes = person["hours"]
        days = ", ".join(DAY_NAMES[day] for day in person["days"])
        st.write(f"**Working hours** · {days} · {opens:02d}:00–{closes:02d}:00")
        if person["offer"]:
            percent, first_hour, last_hour = person["offer"]
            st.success(
                f"Save {percent}% on labour for visits starting between "
                f"{first_hour:02d}:00 and {last_hour:02d}:00 on working days."
            )

    with right, st.container(border=True):
        st.subheader(service)
        st.write(f"Visit area · {area}")
        st.metric("Standard hourly rate", f"CHF {rate(person, service)}")
        if first:
            st.caption(f"Next opening · {first:%a %d.%m at %H:%M}")
        if st.button("Choose date & extras", type="primary", width="stretch"):
            start_checkout(state.get("lc_preferred_slot") or first)
        if offer and st.button(f"Use discount slot · {offer:%d.%m %H:%M}", width="stretch"):
            start_checkout(offer)
        st.link_button(
            "Directions in Google Maps",
            maps_url(
                "dir", origin=f"{person['base']}, Switzerland",
                destination=f"{area}, Switzerland", travelmode="driving",
            ),
        )


def checkout():
    back(PROFILE_PAGE)
    choice = state.get("lc_choice")
    if not choice:
        st.info("Choose a cleaner before requesting a visit.")
        return

    key, service, area = choice["cleaner"], choice["service"], choice["area"]
    person = CLEANERS[key]
    minimum = SERVICES[service][0]
    hourly = rate(person, service)
    today = now().date()
    preferred = state.get("lc_preferred_slot")
    first, _ = next_openings(key, service)
    default_day = first.date() if first else today + timedelta(days=1)
    if preferred and today <= preferred.date() <= today + timedelta(days=90):
        default_day = preferred.date()
    version = state.lc_checkout_version

    st.title("Review your visit")
    st.write(f"{service} with **{person['name']}** in {area}")
    details, summary = st.columns([3, 2], gap="large")

    with details:
        hours = st.slider("Estimated cleaning hours", minimum, 8, minimum, key=f"hours_{version}")
        extras = st.multiselect(
            "Extras", list(EXTRAS), key=f"extras_{version}",
            format_func=lambda item: f"{item} (+CHF {EXTRAS[item]})",
        )
        a, b = st.columns(2)
        with a:
            day = st.date_input(
                "Visit date", value=default_day, min_value=today,
                max_value=today + timedelta(days=90), format="DD.MM.YYYY", key=f"day_{version}",
            )
        slots = slots_for(key, day, hours)
        with b:
            starts = st.selectbox(
                "Start time · Swiss local time",
                slots,
                index=slots.index(preferred) if preferred in slots else (0 if slots else None),
                format_func=lambda slot: (
                    f"{slot:%H:%M} · {discount_for(person, slot)}% off"
                    if discount_for(person, slot) else f"{slot:%H:%M}"
                ),
                placeholder="No openings", key=f"slot_{version}_{day}_{hours}",
            )
        if not slots:
            st.info("Try another date or a shorter visit.")

        st.subheader("Address and payment")
        addresses = {
            address_id: item["label"] for address_id, item in state.lc_addresses.items()
            if item["area"] == area
        }
        address_choices = [None, *addresses]
        preferred_address = state.get("lc_preferred_address")
        address = st.selectbox(
            "Visit address", address_choices,
            index=address_choices.index(preferred_address) if preferred_address in addresses else 0,
            format_func=lambda value: addresses.get(value, f"Use {area} only"),
        )
        card = st.selectbox(
            "Payment method", [None, *state.lc_cards],
            format_func=lambda value: state.lc_cards.get(value, "Pay after service · demo"),
        )
        st.page_link(ADDRESSES_PAGE, label="Manage saved addresses")
        st.page_link(PAYMENTS_PAGE, label="Manage payment methods")

    labour = hours * hourly * 100
    percent = discount_for(person, starts)
    discount = labour * percent // 100
    total = labour - discount + sum(EXTRAS[item] * 100 for item in extras)

    with summary, st.container(border=True):
        st.subheader("Price breakdown")
        st.write(f"{hours} hours × CHF {hourly} · {money(labour)}")
        if discount:
            st.success(f"Time-slot discount ({percent}%) · −{money(discount)}")
        for item in extras:
            st.write(f"{item} · {money(EXTRAS[item] * 100)}")
        st.divider()
        st.metric("Estimated total", money(total))
        submitted = st.button(
            "Request booking", type="primary", width="stretch", disabled=starts is None
        )
        st.caption("Demo booking · No payment is collected.")

    if submitted:
        if starts not in slots_for(key, day, hours):
            st.error("That start time is no longer available. Choose another slot.")
            return
        order = {
            **choice,
            "id": uuid4().hex[:8].upper(),
            "starts": starts,
            "ends": starts + timedelta(hours=hours),
            "total_cents": total,
            "discount_cents": discount,
            "extras": list(extras),
            "address": addresses.get(address, area),
            "payment": state.lc_cards.get(card, "Pay after service · demo"),
            "status": "Requested",
            "history": [("Requested", now())],
        }
        state.lc_orders.append(order)
        state.lc_order_id = order["id"]
        st.switch_page(DETAIL_PAGE)


def bookings():
    st.title("Bookings")
    completed = [order for order in state.lc_orders if order["status"] == "Completed"]
    a, b, c = st.columns(3)
    a.metric("Total requests", len(state.lc_orders))
    b.metric("Completed services", len(completed))
    c.metric("Total spent · demo", money(sum(order_total(order) for order in completed)))

    groups = {"Upcoming": ACTIVE, "Past services": ("Completed",), "Cancelled": ("Cancelled",)}
    group = st.segmented_control("Booking history", list(groups), default="Upcoming") or "Upcoming"
    results = [order for order in state.lc_orders if order["status"] in groups[group]]
    if not results:
        st.info("No bookings in this section yet.")
        st.page_link(EXPLORE_PAGE, label="Find a cleaner")

    for order in sorted(results, key=lambda item: item["starts"], reverse=group != "Upcoming"):
        with st.container(border=True):
            left, right = st.columns([3, 1])
            with left:
                st.write(f"**{order['service']} · {CLEANERS[order['cleaner']]['name']}**")
                st.write(f"{order['area']} · {visit_label(order)}")
                st.caption(f"{order['status']} · Reference {order['id']}")
            with right:
                st.write(f"**{money(order_total(order))}**")
                if st.button("View details", key=f"view_{order['id']}", width="stretch"):
                    state.lc_order_id = order["id"]
                    st.switch_page(DETAIL_PAGE)


def booking_detail():
    back(BOOKINGS_PAGE)
    order = next(
        (item for item in state.lc_orders if item["id"] == state.get("lc_order_id")), None
    )
    if order is None:
        st.info("Open a booking from your booking history.")
        return

    status = order["status"]
    st.title(order["service"])
    st.write(f"With **{CLEANERS[order['cleaner']]['name']}** · {visit_label(order)}")
    left, right = st.columns(2, gap="large")

    with left, st.container(border=True):
        st.subheader("Visit details")
        location = order["area"]
        if order["address"] != location:
            location = f"{order['address']} · {location}"
        st.text(location)
        st.write(f"**{money(order_total(order))}** · {order['payment']}")
        if order.get("discount_cents"):
            st.caption(f"Discount applied · {money(order['discount_cents'])}")
        if order["extras"]:
            st.caption("Extras · " + ", ".join(order["extras"]))
        st.caption(f"Reference · {order['id']}")
        if status in ACTIVE:
            st.download_button(
                "Add to calendar (.ics)", calendar_file(order),
                file_name=f"luzern-clean-{order['id'].lower()}.ics", mime="text/calendar",
            )

    with right, st.container(border=True):
        st.subheader(status)
        if status in STATUSES:
            step = STATUSES.index(status)
            st.progress((step + 1) / len(STATUSES))
            if status in ACTIVE:
                following = STATUSES[step + 1]
                st.button(
                    f"Demo · mark as {following.lower()}",
                    on_click=set_status, args=(order, following),
                )
        if status in ("Requested", "Confirmed"):
            st.button("Cancel booking", on_click=set_status, args=(order, "Cancelled"))
        if status in ("Completed", "Cancelled") and st.button("Book again", type="primary"):
            state.lc_choice = {key: order[key] for key in ("cleaner", "area", "service")}
            state.lc_preferred_address = None
            start_checkout()
        with st.expander("Status history"):
            for event, timestamp in reversed(order["history"]):
                st.write(f"**{event}** · {timestamp:%d.%m.%Y %H:%M}")

    if status == "Completed":
        st.subheader("Rate your visit")
        with st.form(f"feedback_{order['id']}"):
            score = st.slider("Stars", 1, 5, value=order.get("review_rating", 5))
            note = st.text_area("Private feedback", order.get("review_note", ""), max_chars=400)
            if st.form_submit_button("Save feedback"):
                order["review_rating"] = score
                order["review_note"] = note.strip()
                st.success("Feedback saved for this session.")


def account():
    st.title("Account")
    if state.lc_personal["name"]:
        st.text(state.lc_personal["name"])
    for label, description, page in [
        ("Personal info", "Name, email and phone", PERSONAL_PAGE),
        ("Saved addresses", f"{len(state.lc_addresses)} saved", ADDRESSES_PAGE),
        ("Payment methods", f"{len(state.lc_cards)} demo cards", PAYMENTS_PAGE),
        ("Account settings", "Language and reminder preferences", SETTINGS_PAGE),
    ]:
        with st.container(border=True):
            st.page_link(page, label=label)
            st.caption(description)


def personal():
    back(ACCOUNT_PAGE)
    st.title("Personal info")
    st.caption("Use sample details in this demo.")
    current = state.lc_personal
    with st.form("personal"):
        name = st.text_input("Full name", current["name"], max_chars=80)
        email = st.text_input("Email", current["email"], max_chars=120)
        phone = st.text_input("Phone", current["phone"], max_chars=30)
        if st.form_submit_button("Save changes", type="primary"):
            email = email.strip()
            local, separator, domain = email.partition("@")
            if email and (not separator or not local or "." not in domain or any(c.isspace() for c in email)):
                st.error("Enter an email such as name@example.com.")
            else:
                state.lc_personal = {"name": name.strip(), "email": email, "phone": phone.strip()}
                st.success("Personal info saved for this session.")


def addresses():
    back(ACCOUNT_PAGE)
    st.title("Saved addresses")
    st.caption("Save a label such as Home or Office and a municipality.")
    for key, item in list(state.lc_addresses.items()):
        with st.container(border=True):
            st.text(f"{item['label']} · {item['area']}")
            if st.button("Remove", key=f"remove_address_{key}"):
                del state.lc_addresses[key]
                st.rerun()

    with st.form("add_address"):
        label = st.text_input("Address label", max_chars=50)
        area = st.selectbox("Municipality", list(AREAS))
        if st.form_submit_button("Add address", type="primary"):
            if label.strip():
                state.lc_addresses[uuid4().hex] = {"label": label.strip(), "area": area}
                st.rerun()
            st.error("Enter an address label.")


def payments():
    back(ACCOUNT_PAGE)
    st.title("Payment methods")
    st.caption("Choose a sample card for this demo.")
    for brand, label in list(state.lc_cards.items()):
        with st.container(border=True):
            st.write(label)
            if st.button("Remove", key=f"remove_card_{brand}"):
                del state.lc_cards[brand]
                st.rerun()

    available = [brand for brand in DEMO_CARDS if brand not in state.lc_cards]
    if available:
        with st.form("add_card"):
            brand = st.selectbox("Sample card", available)
            if st.form_submit_button("Add payment method", type="primary"):
                state.lc_cards[brand] = f"{brand} ···· {DEMO_CARDS[brand]}"
                st.rerun()


def settings():
    back(ACCOUNT_PAGE)
    st.title("Account settings")
    st.caption("The demo stores your preferences for this session. The interface is in English.")
    languages = ["English", "Deutsch", "Türkçe"]
    with st.form("settings"):
        language = st.selectbox(
            "Preferred language", languages,
            index=languages.index(state.lc_preferences["language"]),
        )
        reminders = st.toggle("Booking reminders", value=state.lc_preferences["reminders"])
        if st.form_submit_button("Save settings", type="primary"):
            state.lc_preferences = {"language": language, "reminders": reminders}
            st.success("Preferences saved.")


def about():
    hero(
        "About Luzern Clean",
        "A local platform for finding and booking home cleaning around Lucerne.",
    )

    left, right = st.columns(2, gap="large")
    with left, st.container(border=True):
        st.subheader("Our mission")
        st.write(
            "Make home cleaning easier to arrange by connecting households with local "
            "cleaners through clear pricing, service details and flexible scheduling."
        )
    with right, st.container(border=True):
        st.subheader("Our vision")
        st.write(
            "Build a trusted regional platform where households can book repeat visits "
            "with confidence and independent cleaners can grow a local client base."
        )

    st.subheader("Leadership team")
    for offset in range(0, len(TEAM), 3):
        for column, (name, role, description) in zip(st.columns(3), TEAM[offset:offset + 3]):
            with column, st.container(border=True):
                identity(name, role)
                st.write(description)

    st.subheader("How we work")
    principles = [
        ("Transparent pricing", "Review hours, extras and applicable discounts before booking."),
        ("Local coverage", "Choose cleaners by municipality, services, languages and pet policy."),
        ("Consistent service", "Our proposed onboarding uses service standards and a practical assessment."),
    ]
    for column, (title, description) in zip(st.columns(3), principles):
        with column, st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(description)

    with st.expander("Frequently asked questions"):
        st.markdown("**Where is the platform designed to operate?**")
        st.write(", ".join(AREAS) + ".")
        st.markdown("**How are discounts calculated?**")
        st.write("Eligible start times reduce the labour subtotal. Extras are charged at their listed prices.")
        st.markdown("**Can I apply as an independent cleaner?**")
        st.write("Yes. The demo application lets you choose the areas and services you would offer.")

    left, right = st.columns(2)
    with left:
        st.page_link(MAP_PAGE, label="See service coverage", icon=":material/map:")
    with right:
        st.page_link(JOIN_PAGE, label="Become a cleaner", icon=":material/person_add:")


def become_cleaner():
    hero(
        "Become a certified cleaner",
        "Apply to join the Luzern Clean network and offer services in your area.",
    )
    left, right = st.columns([2, 3], gap="large")

    with left:
        st.subheader("How onboarding works")
        steps = [
            ("Apply", "Tell us where you work and which services you offer."),
            ("Meet the team", "Discuss availability, experience and service expectations."),
            ("Complete an assessment", "Walk through a sample visit and the service checklist."),
            ("Platform approval", "Approved cleaners can publish their profile and availability."),
        ]
        for title, description in steps:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.write(description)
        st.caption("This is the proposed platform onboarding process. The demo does not issue certification.")

    with right, st.container(border=True):
        st.subheader("Cleaner application")
        st.caption("Use sample details. Applications stay in this session.")
        with st.form("cleaner_application"):
            a, b = st.columns(2)
            with a:
                name = st.text_input("Full name", max_chars=80)
                experience = st.selectbox(
                    "Cleaning experience", ["New to professional cleaning", "Under 1 year", "1–3 years", "4+ years"]
                )
            with b:
                email = st.text_input("Email", max_chars=120)
                pets = st.multiselect("Pets you can work around", ["Dogs", "Cats"])

            areas = st.multiselect("Where can you work?", list(AREAS))
            services = st.multiselect("Which services do you offer?", list(SERVICES))
            notes = st.text_area("Tell us a little about your work", max_chars=500)
            submitted = st.form_submit_button("Submit demo application", type="primary", width="stretch")

        if submitted:
            email = email.strip()
            local, separator, domain = email.partition("@")
            if not name.strip() or not areas or not services:
                st.error("Enter your name and select at least one area and service.")
            elif not separator or not local or "." not in domain or any(c.isspace() for c in email):
                st.error("Enter a sample email such as name@example.com.")
            elif any(item["email"].casefold() == email.casefold() for item in state.lc_applications):
                st.info("An application with this email already exists in this session.")
            else:
                reference = f"LC-{uuid4().hex[:6].upper()}"
                state.lc_applications.append({
                    "reference": reference, "name": name.strip(), "email": email,
                    "areas": areas, "services": services, "experience": experience,
                    "pets": pets, "notes": notes.strip(),
                })
                st.success(f"Demo application saved · Reference {reference}")

    if state.lc_applications:
        st.subheader("Applications in this session")
        for item in reversed(state.lc_applications):
            with st.container(border=True):
                st.text(f"{item['name']} · {item['reference']}")
                st.caption("Application saved · " + ", ".join(item["areas"]))


EXPLORE_PAGE = st.Page(explore, title="Explore", icon=":material/explore:", default=True)
MAP_PAGE = st.Page(service_map, title="Service Map", icon=":material/map:", url_path="service-map")
BOOKINGS_PAGE = st.Page(bookings, title="Bookings", icon=":material/calendar_month:", url_path="bookings")
ACCOUNT_PAGE = st.Page(account, title="Account", icon=":material/person:", url_path="account")
ABOUT_PAGE = st.Page(about, title="About Us", icon=":material/business:", url_path="about")
JOIN_PAGE = st.Page(become_cleaner, title="Become a Cleaner", icon=":material/person_add:", url_path="become-a-cleaner")
PROFILE_PAGE = st.Page(profile, title="Cleaner profile", url_path="cleaner")
CHECKOUT_PAGE = st.Page(checkout, title="Review visit", url_path="review")
DETAIL_PAGE = st.Page(booking_detail, title="Booking details", url_path="booking")
PERSONAL_PAGE = st.Page(personal, title="Personal info", url_path="personal-info")
ADDRESSES_PAGE = st.Page(addresses, title="Saved addresses", url_path="addresses")
PAYMENTS_PAGE = st.Page(payments, title="Payment methods", url_path="payments")
SETTINGS_PAGE = st.Page(settings, title="Account settings", url_path="settings")

MAIN_PAGES = [EXPLORE_PAGE, MAP_PAGE, BOOKINGS_PAGE, ACCOUNT_PAGE, ABOUT_PAGE, JOIN_PAGE]
page = st.navigation(
    [
        *MAIN_PAGES, PROFILE_PAGE, CHECKOUT_PAGE, DETAIL_PAGE,
        PERSONAL_PAGE, ADDRESSES_PAGE, PAYMENTS_PAGE, SETTINGS_PAGE,
    ],
    position="hidden",
)

st.html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Instrument+Serif&display=swap');

    :root { --lc-ink: #172e25; --lc-green: #1c6048; --lc-muted: #506c5e; }
    .stApp, [data-testid="stHeader"] { background: #f4f7f2; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1200px;
        padding-top: 2.6rem;
        padding-bottom: 3rem;
        font-family: "DM Sans", sans-serif;
        color: var(--lc-ink);
    }
    [data-testid="stMainBlockContainer"] :is(h1,h2,h3,p,label) { color: var(--lc-ink); }
    [data-testid="stPageLink"] a { border-radius: 12px; }
    [data-testid="stPageLink"] a:hover { background: #e3efe6; }
    .lc-brand {
        display: inline-flex;
        align-items: center;
        gap: .65rem;
        color: var(--lc-ink);
        font-weight: 700;
        font-size: 1.3rem;
    }
    .lc-brand span, .lc-identity > span { display: grid; place-items: center; }
    .lc-brand span {
        width: 38px; height: 38px;
        background: var(--lc-green); color: white; border-radius: 12px;
        font-size: .92rem;
    }
    .lc-hero {
        padding: clamp(28px, 6vw, 66px);
        border-radius: 26px;
        background: radial-gradient(ellipse at 95% 0%, #4a8e6f, transparent 58%),
                    linear-gradient(125deg, #103126, #225840);
    }
    .lc-hero h1 {
        color: white !important;
        font: 400 clamp(2.8rem, 7vw, 5.3rem)/.98 "Instrument Serif", Georgia, serif;
        margin: 0;
        padding: 0;
    }
    .lc-hero p { margin: 14px 0 0; color: #e5f1e8 !important; max-width: 56ch; }
    .lc-identity { display: flex; align-items: center; gap: 12px; }
    .lc-identity > span {
        width: 48px; height: 48px;
        flex: 0 0 48px;
        background: #e0eee4; color: #185940; border-radius: 15px;
        font-weight: 700;
    }
    .lc-identity strong { display: block; font-size: 1.12rem; color: var(--lc-ink); }
    .lc-identity small { display: block; color: var(--lc-muted); }
    .lc-offer {
        display: inline-block;
        padding: 5px 10px;
        background: #e1f0e4;
        color: #154932;
        border-radius: 999px;
        font-size: .84rem;
        font-weight: 700;
    }
    [data-testid="stVerticalBlockBorderWrapper"] { background: #fff; border-radius: 17px; }
    button[kind="primary"] {
        background: var(--lc-green); color: #fff; border-color: var(--lc-green);
    }
    button[kind="primary"]:hover { background: #164a38; color: #fff; border-color: #164a38; }
    @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"] { padding-top: 2rem; }
        .lc-hero { border-radius: 18px; }
    }
    </style>
    <div class="lc-brand"><span>LC</span>Luzern Clean</div>
    """
)

for column, destination in zip(st.columns([1, 1.2, 1, 1, 1, 1.6]), MAIN_PAGES):
    with column:
        st.page_link(destination, width="stretch")

st.divider()
page.run()
st.divider()
st.caption("Luzern Clean · Platform demo · Sample profiles and prices · Session-only data")
