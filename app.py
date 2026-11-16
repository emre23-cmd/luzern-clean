from datetime import datetime, time, timedelta, timezone
from urllib.parse import urlencode
from uuid import uuid4
from zoneinfo import ZoneInfo

import streamlit as st


st.set_page_config(page_title="Luzern Clean", page_icon="🌿", layout="wide")

SWISS_TZ = ZoneInfo("Europe/Zurich")

AREAS = {
    "Luzern": (47.0502, 8.3093),
    "Meggen": (47.0465, 8.3740),
    "Greppen": (47.0561, 8.4299),
    "Weggis": (47.0321, 8.4337),
    "Vitznau": (47.0106, 8.4839),
    "Küssnacht am Rigi": (47.0830, 8.4410),
}

SERVICES = {
    "Regular home cleaning": (2, 45, "Kitchens, bathrooms, floors and everyday surfaces."),
    "Deep cleaning": (3, 55, "Extra attention to buildup and hard-to-reach areas."),
    "Move-out cleaning": (4, 60, "A thorough clean for an empty home before handover."),
}

EXTRAS = {
    "Bring cleaning supplies": 12,
    "Inside the oven": 25,
    "Inside the fridge": 20,
}

REGULAR = "Regular home cleaning"
DEEP = "Deep cleaning"
MOVE_OUT = "Move-out cleaning"
ALL_SERVICES = tuple(SERVICES)
ALL_AREAS = tuple(AREAS)
WEEKDAYS = (0, 1, 2, 3, 4)
MON_SAT = (0, 1, 2, 3, 4, 5)
EVERY_DAY = tuple(range(7))
DAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
BOTH_PETS = ("Dogs", "Cats")
STATUS_FLOW = ("Requested", "Confirmed", "On the way", "In progress", "Completed")
ACTIVE_STATUSES = STATUS_FLOW[:-1]
DEMO_CARDS = {"Visa": "4242", "Mastercard": "4444"}


def cleaner(
    name, base, areas, services, languages, rating, jobs, premium, pets,
    days, working_hours, offer, bio,
):
    return {
        "name": name,
        "base": base,
        "areas": areas,
        "services": services,
        "languages": languages,
        "rating": rating,
        "jobs": jobs,
        "premium": premium,
        "pets": pets,
        "days": days,
        "working_hours": working_hours,
        "offer": offer,
        "bio": bio,
    }


# Offer format: (discount percent, first start hour, last start hour).
CLEANERS = {
    "sofia": cleaner(
        "Sofia M.", "Luzern", ("Luzern", "Meggen", "Greppen"),
        (REGULAR, DEEP), ("English", "German", "Portuguese"), 4.9, 126, 0,
        BOTH_PETS, WEEKDAYS, (8, 18), (15, 11, 14),
        "Focuses on recurring home visits and detailed kitchen cleans.",
    ),
    "lea": cleaner(
        "Lea K.", "Weggis", ("Weggis", "Vitznau", "Greppen", "Meggen"),
        ALL_SERVICES, ("English", "German", "French"), 4.8, 94, 4,
        ("Cats",), MON_SAT, (8, 18), None,
        "Specialises in handover cleans around the lakeside communities.",
    ),
    "amina": cleaner(
        "Amina B.", "Küssnacht am Rigi",
        ("Küssnacht am Rigi", "Greppen", "Weggis", "Vitznau"),
        (REGULAR, DEEP), ("English", "German", "Arabic"), 4.9, 74, 2,
        BOTH_PETS, MON_SAT, (9, 18), (10, 13, 15),
        "Offers recurring visits and one-off deep cleans around Mount Rigi.",
    ),
    "daniel": cleaner(
        "Daniel R.", "Meggen", ("Luzern", "Meggen", "Küssnacht am Rigi"),
        (DEEP, MOVE_OUT), ("English", "German", "Spanish"), 4.8, 113, 5,
        ("Dogs",), WEEKDAYS, (8, 19), None,
        "Works on larger apartments and end-of-tenancy cleaning.",
    ),
    "elif": cleaner(
        "Elif A.", "Greppen", ALL_AREAS, ALL_SERVICES,
        ("English", "German", "Turkish"), 4.9, 82, 3,
        BOTH_PETS, MON_SAT, (8, 19), (10, 10, 12),
        "Handles regular visits and move-out cleans across the service area.",
    ),
    "maya": cleaner(
        "Maya L.", "Luzern", ("Luzern", "Meggen", "Küssnacht am Rigi"),
        (REGULAR, DEEP), ("English", "German", "Italian"), 4.9, 68, 1,
        BOTH_PETS, (1, 2, 3, 4, 5), (8, 18), (20, 9, 11),
        "Offers morning appointments and has experience working in homes with pets.",
    ),
    "jonas": cleaner(
        "Jonas F.", "Küssnacht am Rigi",
        ("Küssnacht am Rigi", "Greppen", "Weggis", "Meggen"),
        ALL_SERVICES, ("English", "German"), 4.7, 57, -2,
        ("Dogs",), MON_SAT, (9, 19), (15, 13, 15),
        "Focuses on practical weekly cleaning and flexible afternoon visits.",
    ),
    "nina": cleaner(
        "Nina P.", "Vitznau", ("Vitznau", "Weggis", "Greppen"),
        (REGULAR, DEEP), ("English", "German", "French"), 4.8, 61, 2,
        ("Cats",), (3, 4, 5, 6), (9, 18), None,
        "Offers weekend bookings and detailed cleaning for smaller homes.",
    ),
    "samir": cleaner(
        "Samir H.", "Luzern", ("Luzern", "Meggen", "Greppen"),
        ALL_SERVICES, ("English", "German", "Arabic"), 4.9, 91, 4,
        BOTH_PETS, EVERY_DAY, (10, 20), (15, 15, 17),
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
state.setdefault("lc_filter", {
    "area": "Luzern",
    "service": REGULAR,
    "pets": "Any",
    "language": "Any",
    "sort": "Smart match",
    "offers_only": False,
    "favourites_only": False,
    "view": "Split",
})


def swiss_now():
    return datetime.now(SWISS_TZ)


def money(cents):
    return f"CHF {cents / 100:,.2f}"


def maps_url(action, **params):
    return f"https://www.google.com/maps/{action}/?{urlencode({'api': 1, **params})}"


def hourly_rate(person, service):
    return SERVICES[service][1] + person["premium"]


def offer_percent(person, start):
    offer = person["offer"]
    if offer and offer[1] <= start.hour <= offer[2]:
        return offer[0]
    return 0


def visit_label(order):
    return f"{order['starts']:%d.%m.%Y · %H:%M}–{order['ends']:%H:%M}"


def pet_label(person):
    if person["pets"] == BOTH_PETS:
        return "Dogs & cats welcome"
    return f"{person['pets'][0]} welcome"


def available_slots(cleaner_id, day, hours):
    person = CLEANERS[cleaner_id]
    if day.weekday() not in person["days"]:
        return []

    opens, closes = person["working_hours"]
    now = swiss_now()
    active_orders = [
        order for order in state.lc_orders
        if order["cleaner"] == cleaner_id and order["status"] in ACTIVE_STATUSES
    ]
    result = []

    for hour in range(opens, closes - hours + 1):
        starts = datetime.combine(day, time(hour), tzinfo=SWISS_TZ)
        ends = starts + timedelta(hours=hours)
        occupied = any(
            starts < order["ends"] and ends > order["starts"]
            for order in active_orders
        )
        if starts > now and not occupied:
            result.append(starts)

    return result


def week_availability(cleaner_id, service):
    minimum_hours = SERVICES[service][0]
    today = swiss_now().date()
    slots = [
        slot
        for offset in range(7)
        for slot in available_slots(
            cleaner_id, today + timedelta(days=offset), minimum_hours
        )
    ]
    person = CLEANERS[cleaner_id]
    discounted = next((slot for slot in slots if offer_percent(person, slot)), None)
    return (slots[0] if slots else None), discounted


def change_status(order, status):
    order["status"] = status
    order["history"].append((status, swiss_now()))


def toggle_favourite(cleaner_id):
    if cleaner_id in state.lc_favourites:
        state.lc_favourites.remove(cleaner_id)
    else:
        state.lc_favourites.add(cleaner_id)


def cleaner_header(person):
    # All HTML fields below come from the fixed demo catalogue.
    initials = "".join(part[0] for part in person["name"].split())
    st.html(
        f"""
        <div class="lc-person">
            <div class="lc-avatar">{initials}</div>
            <div><strong>{person['name']}</strong><small>{person['base']}</small></div>
        </div>
        """
    )


def back(label, destination):
    if st.button(label, key=f"back_{destination.url_path}"):
        st.switch_page(destination)


def calendar_file(order):
    def utc_stamp(value):
        return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    return "\r\n".join([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Luzern Clean//Demo Bookings//EN",
        "BEGIN:VEVENT",
        f"UID:{order['id']}@luzern-clean.demo",
        f"DTSTAMP:{utc_stamp(order['history'][0][1])}",
        f"DTSTART:{utc_stamp(order['starts'])}",
        f"DTEND:{utc_stamp(order['ends'])}",
        "SUMMARY:Luzern Clean demo visit",
        f"LOCATION:{order['area']}",
        "END:VEVENT",
        "END:VCALENDAR",
        "",
    ])


def explore():
    st.html(
        """
        <div class="lc-hero">
            <h1>Where do you need cleaning?</h1>
            <p>Compare local cleaners, find a time slot and see your price upfront.</p>
        </div>
        """
    )

    filters = state.lc_filter
    languages = ["Any", *sorted({
        language for person in CLEANERS.values() for language in person["languages"]
    })]
    pet_options = ["Any", "Dogs", "Cats", "Dogs & cats"]
    sort_options = ["Smart match", "Lowest hourly rate", "Soonest opening", "Top rated"]

    a, b, c, d = st.columns(4)
    with a:
        area = st.selectbox("Visit area", ALL_AREAS, index=ALL_AREAS.index(filters["area"]))
    with b:
        service = st.selectbox(
            "Service", ALL_SERVICES, index=ALL_SERVICES.index(filters["service"])
        )
    with c:
        pet = st.selectbox("Pets at home", pet_options, index=pet_options.index(filters["pets"]))
    with d:
        language = st.selectbox(
            "Cleaner language", languages, index=languages.index(filters["language"])
        )

    st.caption(SERVICES[service][2])
    a, b, c = st.columns([2, 1, 1])
    with a:
        order_by = st.selectbox("Sort by", sort_options, index=sort_options.index(filters["sort"]))
    with b:
        offers_only = st.toggle("Discount slots only", value=filters["offers_only"])
    with c:
        favourites_only = st.toggle("Favourites only", value=filters["favourites_only"])

    views = ["Split", "List", "Map"]
    view = st.segmented_control(
        "Results view", views, default=filters["view"]
    ) or "Split"

    state.lc_filter = {
        "area": area, "service": service, "pets": pet, "language": language,
        "sort": order_by, "offers_only": offers_only,
        "favourites_only": favourites_only, "view": view,
    }

    required_pets = {
        "Any": set(), "Dogs": {"Dogs"}, "Cats": {"Cats"}, "Dogs & cats": set(BOTH_PETS),
    }[pet]
    matches = []
    for key, person in CLEANERS.items():
        if (
            area not in person["areas"]
            or service not in person["services"]
            or (language != "Any" and language not in person["languages"])
            or not required_pets.issubset(person["pets"])
            or (favourites_only and key not in state.lc_favourites)
        ):
            continue

        first, discounted = week_availability(key, service)
        if offers_only and discounted is None:
            continue
        matches.append((key, person, first, discounted))

    latest = datetime.max.replace(tzinfo=SWISS_TZ)
    ranking = {
        "Smart match": lambda row: (
            row[2] is None, row[3] is None, -row[1]["rating"], -row[1]["jobs"]
        ),
        "Lowest hourly rate": lambda row: hourly_rate(row[1], service),
        "Soonest opening": lambda row: row[2] or latest,
        "Top rated": lambda row: (-row[1]["rating"], -row[1]["jobs"]),
    }
    matches.sort(key=ranking[order_by])

    if view == "Split":
        listing, map_panel = st.columns([1, 1], gap="large")
    else:
        listing = map_panel = st.container()

    if view != "Map":
        with listing:
            st.subheader(f"{len(matches)} matching cleaners")
            if not matches:
                st.info("No matches. Try another service, area or filter.")

            for key, person, first, discounted in matches:
                with st.container(border=True):
                    cleaner_header(person)
                    st.write(
                        f"**★ {person['rating']:.1f}** · {person['jobs']} jobs · "
                        f"**CHF {hourly_rate(person, service)}/h**"
                    )
                    st.caption(f"{pet_label(person)} · " + ", ".join(person["languages"]))
                    if first:
                        st.caption(f"Next opening · {first:%a %d.%m · %H:%M}")
                    if discounted:
                        st.html(
                            f'<span class="lc-offer">Save {offer_percent(person, discounted)}% '
                            f'· {discounted:%a %d.%m at %H:%M}</span>'
                        )

                    profile_col, save_col = st.columns([3, 1])
                    with profile_col:
                        if st.button("View profile", key=f"profile_{key}", width="stretch"):
                            state.lc_choice = {"cleaner": key, "area": area, "service": service}
                            state.lc_preferred_slot = discounted if offers_only else first
                            st.switch_page(PROFILE_PAGE)
                    with save_col:
                        st.button(
                            "♥ Saved" if key in state.lc_favourites else "♡ Save",
                            key=f"favourite_{key}",
                            on_click=toggle_favourite,
                            args=(key,),
                            width="stretch",
                        )

    if view != "List":
        with map_panel:
            st.subheader("Service map")
            places = list(dict.fromkeys([area, *(row[1]["base"] for row in matches)]))
            st.map(
                {
                    "lat": [AREAS[place][0] for place in places],
                    "lon": [AREAS[place][1] for place in places],
                    "pin": ["#176145" if place == area else "#DB844A" for place in places],
                },
                latitude="lat", longitude="lon", color="pin", size=240, height=410,
            )
            st.caption("Green · Your service area. Orange · Cleaner base towns.")
            st.link_button(
                "Open area in Google Maps",
                maps_url("search", query=f"{area}, Switzerland"),
                width="stretch",
            )


def profile():
    back("← Explore", EXPLORE_PAGE)
    choice = state.get("lc_choice")
    if not choice:
        st.info("Open a cleaner from Explore to see the profile.")
        return

    key, area, service = choice["cleaner"], choice["area"], choice["service"]
    person = CLEANERS[key]
    first, discounted = week_availability(key, service)
    info, actions = st.columns([3, 2], gap="large")

    with info:
        st.title(person["name"])
        cleaner_header(person)
        st.write(f"**★ {person['rating']:.1f}** · {person['jobs']} sample completed jobs")
        st.write(person["bio"])
        st.write(f"**Pet policy** · {pet_label(person)}")
        st.write("**Languages** · " + ", ".join(person["languages"]))
        st.write("**Services** · " + ", ".join(person["services"]))
        st.write("**Coverage** · " + ", ".join(person["areas"]))
        opens, closes = person["working_hours"]
        st.write(
            "**Working hours** · "
            + ", ".join(DAY_NAMES[day] for day in person["days"])
            + f" · {opens:02d}:00–{closes:02d}:00"
        )
        if person["offer"]:
            percent, start_hour, end_hour = person["offer"]
            st.success(
                f"Save {percent}% on cleaning labour when the visit starts "
                f"from {start_hour:02d}:00 through {end_hour:02d}:00 on a working day."
            )

    with actions:
        with st.container(border=True):
            st.subheader(service)
            st.write(f"Visit area · {area}")
            st.metric("Standard hourly rate", f"CHF {hourly_rate(person, service)}")
            if first:
                st.caption(f"Next opening · {first:%a %d.%m at %H:%M}")
            if st.button("Choose date & extras", type="primary", width="stretch"):
                st.switch_page(CHECKOUT_PAGE)
            if discounted and st.button(
                f"Use discount slot · {discounted:%d.%m %H:%M}", width="stretch"
            ):
                state.lc_preferred_slot = discounted
                st.switch_page(CHECKOUT_PAGE)
            st.link_button(
                "Open route in Google Maps",
                maps_url(
                    "dir",
                    origin=f"{person['base']}, Switzerland",
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

    key, service, area = choice["cleaner"], choice["service"], choice["area"]
    person = CLEANERS[key]
    minimum, _, _ = SERVICES[service]
    rate = hourly_rate(person, service)
    today = swiss_now().date()
    preferred = state.get("lc_preferred_slot")
    first, _ = week_availability(key, service)

    default_day = today + timedelta(days=1)
    if first:
        default_day = first.date()
    if preferred and today <= preferred.date() <= today + timedelta(days=90):
        default_day = preferred.date()

    st.title("Review your visit")
    st.write(f"{service} with **{person['name']}** in {area}")
    details, summary = st.columns([3, 2], gap="large")

    with details:
        st.subheader("Visit details")
        hours = st.slider("Estimated cleaning hours", minimum, 8, minimum, key=f"hours_{service}")
        extras = st.multiselect(
            "Extras", list(EXTRAS),
            format_func=lambda name: f"{name} (+CHF {EXTRAS[name]})",
        )

        a, b = st.columns(2)
        with a:
            day = st.date_input(
                "Visit date", value=default_day, min_value=today,
                max_value=today + timedelta(days=90), format="DD.MM.YYYY",
            )
        slots = available_slots(key, day, hours)
        with b:
            starts = st.selectbox(
                "Start time · Swiss local time",
                slots,
                index=slots.index(preferred) if preferred in slots else (0 if slots else None),
                format_func=lambda slot: (
                    f"{slot:%H:%M} · {offer_percent(person, slot)}% off"
                    if offer_percent(person, slot) else f"{slot:%H:%M}"
                ),
                placeholder="No times available",
                key=f"slot_{key}_{day}_{hours}",
            )
        if not slots:
            st.info("No opening for this duration on the selected date.")

        st.subheader("Address and payment")
        address_options = {
            address_id: address["label"]
            for address_id, address in state.lc_addresses.items()
            if address["area"] == area
        }
        address_id = st.selectbox(
            "Visit address",
            [None, *address_options],
            format_func=lambda value: address_options.get(value, f"Use {area} only"),
        )
        card = st.selectbox(
            "Payment method",
            [None, *state.lc_cards],
            format_func=lambda value: state.lc_cards.get(value, "Pay after service · demo"),
        )
        st.page_link(ACCOUNT_PAGE, label="Manage addresses and payment methods")

    labour = hours * rate * 100
    percent = offer_percent(person, starts) if starts else 0
    discount = labour * percent // 100
    total = labour - discount + sum(EXTRAS[name] * 100 for name in extras)

    with summary:
        with st.container(border=True):
            st.subheader("Price breakdown")
            st.write(f"{hours} hours × CHF {rate} · {money(labour)}")
            if discount:
                st.success(f"Time-slot discount ({percent}%) · −{money(discount)}")
            for name in extras:
                st.write(f"{name} · {money(EXTRAS[name] * 100)}")
            st.divider()
            st.metric("Estimated total", money(total))
            submitted = st.button(
                "Request booking", type="primary", width="stretch", disabled=starts is None
            )
            st.caption("Demo booking · No payment is collected.")

    if submitted:
        if starts not in available_slots(key, day, hours):
            st.error("That start time is no longer available. Choose another slot.")
            return

        booking = {
            **choice,
            "id": uuid4().hex[:8].upper(),
            "starts": starts,
            "ends": starts + timedelta(hours=hours),
            "total_cents": total,
            "discount_cents": discount,
            "extras": list(extras),
            "address": address_options.get(address_id, area),
            "payment": state.lc_cards.get(card, "Pay after service · demo"),
            "status": "Requested",
            "history": [("Requested", swiss_now())],
        }
        state.lc_orders.append(booking)
        state.lc_order_id = booking["id"]
        st.switch_page(DETAIL_PAGE)


def order_total(order):
    # Support orders created by the previous app.py in the same session.
    if "total_cents" in order:
        return order["total_cents"]
    return round(order["total"] * 100)


def bookings():
    st.title("Bookings")
    completed = [order for order in state.lc_orders if order["status"] == "Completed"]
    a, b, c = st.columns(3)
    a.metric("Total requests", len(state.lc_orders))
    b.metric("Completed services", len(completed))
    c.metric("Total spent · demo", money(sum(order_total(order) for order in completed)))

    groups = {
        "Upcoming": ACTIVE_STATUSES,
        "Past services": ("Completed",),
        "Cancelled": ("Cancelled",),
    }
    group = st.segmented_control(
        "Booking history", list(groups), default="Upcoming"
    ) or "Upcoming"
    matching = [order for order in state.lc_orders if order["status"] in groups[group]]
    if not matching:
        st.info("No bookings in this section yet.")
        st.page_link(EXPLORE_PAGE, label="Find a cleaner")

    for order in sorted(matching, key=lambda item: item["starts"], reverse=group != "Upcoming"):
        with st.container(border=True):
            info, action = st.columns([3, 1])
            with info:
                st.markdown(f"**{order['service']} · {CLEANERS[order['cleaner']]['name']}**")
                st.write(f"{order['area']} · {visit_label(order)}")
                st.caption(f"{order['status']} · {order['id']}")
            with action:
                st.write(f"**{money(order_total(order))}**")
                if st.button("View details", key=f"order_{order['id']}", width="stretch"):
                    state.lc_order_id = order["id"]
                    st.switch_page(DETAIL_PAGE)


def booking_detail():
    back("← Bookings", BOOKINGS_PAGE)
    order = next((
        item for item in state.lc_orders if item["id"] == state.get("lc_order_id")
    ), None)
    if order is None:
        st.info("Open a booking from your booking history.")
        return

    person = CLEANERS[order["cleaner"]]
    status = order["status"]
    st.title(order["service"])
    st.write(f"With **{person['name']}** · {visit_label(order)}")

    visit, activity = st.columns(2, gap="large")
    with visit:
        with st.container(border=True):
            st.subheader("Visit details")
            st.text(order["area"] if order["address"] == order["area"]
                    else f"{order['address']} · {order['area']}")
            st.write(f"**{money(order_total(order))}** · {order['payment']}")
            if order.get("discount_cents"):
                st.caption(f"Discount applied · {money(order['discount_cents'])}")
            if order["extras"]:
                st.caption("Extras · " + ", ".join(order["extras"]))
            st.caption(f"Reference · {order['id']}")

            if status in ACTIVE_STATUSES:
                st.download_button(
                    "Add to calendar (.ics)",
                    calendar_file(order),
                    file_name=f"luzern-clean-{order['id'].lower()}.ics",
                    mime="text/calendar",
                )

    with activity:
        with st.container(border=True):
            st.subheader(status)
            if status in STATUS_FLOW:
                step = STATUS_FLOW.index(status)
                st.progress((step + 1) / len(STATUS_FLOW))
                if status in ACTIVE_STATUSES:
                    next_status = STATUS_FLOW[step + 1]
                    st.button(
                        f"Demo · mark as {next_status.lower()}",
                        on_click=change_status, args=(order, next_status),
                    )

            if status in ("Requested", "Confirmed"):
                st.button("Cancel booking", on_click=change_status, args=(order, "Cancelled"))

            if status in ("Completed", "Cancelled"):
                if st.button("Book again", type="primary"):
                    state.lc_choice = {
                        key: order[key] for key in ("cleaner", "area", "service")
                    }
                    state.lc_preferred_slot = None
                    st.switch_page(CHECKOUT_PAGE)

            with st.expander("Status history"):
                for event, timestamp in reversed(order["history"]):
                    st.write(f"**{event}** · {timestamp:%d.%m.%Y %H:%M}")

    if status == "Completed":
        st.subheader("Rate your visit")
        with st.form(f"review_{order['id']}"):
            rating = st.slider("Stars", 1, 5, value=order.get("review_rating", 5))
            note = st.text_area(
                "Private feedback", value=order.get("review_note", ""), max_chars=400
            )
            if st.form_submit_button("Save feedback"):
                order["review_rating"] = rating
                order["review_note"] = note.strip()
                st.success("Feedback saved in this session.")


def account():
    st.title("Account")
    if state.lc_personal["name"]:
        st.text(state.lc_personal["name"])
    for label, description, destination in [
        ("Personal info", "Name, email and phone", PERSONAL_PAGE),
        ("Saved addresses", f"{len(state.lc_addresses)} saved", ADDRESSES_PAGE),
        ("Payment methods", f"{len(state.lc_cards)} demo cards", PAYMENTS_PAGE),
        ("Account settings", "Language preference and reminders", SETTINGS_PAGE),
    ]:
        with st.container(border=True):
            st.page_link(destination, label=label)
            st.caption(description)


def personal():
    back("← Account", ACCOUNT_PAGE)
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
            if email and (not separator or not local or "." not in domain or " " in email):
                st.error("Enter an email address such as name@example.com.")
            else:
                state.lc_personal = {"name": name.strip(), "email": email, "phone": phone.strip()}
                st.success("Personal info saved for this session.")


def addresses():
    back("← Account", ACCOUNT_PAGE)
    st.title("Saved addresses")
    st.caption("Use a label such as Home or Office and select a municipality.")

    for key, item in list(state.lc_addresses.items()):
        with st.container(border=True):
            st.text(f"{item['label']} · {item['area']}")
            if st.button("Remove", key=f"remove_address_{key}"):
                del state.lc_addresses[key]
                st.rerun()

    with st.form("new_address"):
        label = st.text_input("Address label", max_chars=50)
        area = st.selectbox("Municipality", ALL_AREAS)
        if st.form_submit_button("Add address", type="primary"):
            if not label.strip():
                st.error("Enter an address label.")
            else:
                state.lc_addresses[uuid4().hex] = {"label": label.strip(), "area": area}
                st.rerun()


def payments():
    back("← Account", ACCOUNT_PAGE)
    st.title("Payment methods")
    st.caption("Choose a sample card for the demo.")
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
    back("← Account", ACCOUNT_PAGE)
    st.title("Account settings")
    st.caption("Preferences are saved for this demo session.")
    languages = ["English", "Deutsch", "Türkçe"]
    with st.form("settings"):
        language = st.selectbox(
            "Preferred language",
            languages,
            index=languages.index(state.lc_preferences["language"]),
        )
        reminders = st.toggle("Booking reminders", value=state.lc_preferences["reminders"])
        if st.form_submit_button("Save settings", type="primary"):
            state.lc_preferences = {"language": language, "reminders": reminders}
            st.success("Preferences saved.")


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

    :root {
        --lc-ink: #162d24;
        --lc-green: #1b6148;
        --lc-muted: #4b695b;
    }
    .stApp, [data-testid="stHeader"] { background: #f5f7f2; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1180px;
        padding-top: 2.6rem;
        padding-bottom: 3rem;
        font-family: "DM Sans", sans-serif;
        color: var(--lc-ink);
    }
    [data-testid="stMainBlockContainer"] :is(h1,h2,h3,p,label) {
        color: var(--lc-ink);
    }
    .lc-brand {
        display: inline-flex;
        gap: .55rem;
        align-items: center;
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--lc-ink);
    }
    .lc-brand span {
        display: grid;
        place-items: center;
        width: 34px;
        height: 34px;
        border-radius: 11px;
        background: var(--lc-green);
        color: white;
    }
    .lc-hero {
        padding: clamp(28px, 6vw, 68px);
        border-radius: 28px;
        background: radial-gradient(ellipse at 96% 0%, #4f9876, transparent 58%),
                    linear-gradient(130deg, #102c22, #225840);
    }
    .lc-hero h1 {
        font: 400 clamp(2.7rem, 7vw, 5.4rem)/.98 "Instrument Serif", Georgia, serif;
        margin: 0;
        padding: 0;
        color: #fff !important;
    }
    .lc-hero p { margin: 14px 0 0; color: #e4f0e9 !important; }
    .lc-person { display: flex; align-items: center; gap: 12px; }
    .lc-person strong { color: var(--lc-ink); font-size: 1.15rem; }
    .lc-person small { display: block; color: var(--lc-muted); }
    .lc-avatar {
        display: grid;
        place-items: center;
        width: 52px;
        height: 52px;
        border-radius: 17px;
        background: #dceee2;
        color: #1a5a40;
        font-weight: 700;
    }
    .lc-offer {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: #e2f2e5;
        color: #164b36;
        font-size: .83rem;
        font-weight: 700;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, .72);
        border-radius: 16px;
    }
    button[kind="primary"] {
        background: var(--lc-green);
        border-color: var(--lc-green);
        color: white;
    }
    button[kind="primary"]:hover {
        background: #154c38;
        border-color: #154c38;
        color: white;
    }
    [data-testid="stPageLink"] a {
        border-radius: 12px;
    }
    @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"] { padding-top: 2rem; }
        .lc-hero { border-radius: 20px; }
    }
    </style>
    """
)

st.html('<div class="lc-brand"><span>LC</span>Luzern Clean</div>')
for column, destination in zip(
    st.columns(3), (EXPLORE_PAGE, BOOKINGS_PAGE, ACCOUNT_PAGE)
):
    with column:
        st.page_link(destination, width="stretch")

st.divider()
page.run()
st.divider()
st.caption("Luzern Clean demo · Sample cleaners, availability and prices · Session-only data")
