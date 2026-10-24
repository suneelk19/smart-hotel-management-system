# Centralized Hotel Facilities and Services Configuration
# STEP 5 - AI Hotel Facilities and Services

HOTEL_FACILITIES = [
    {
        "name": "Free Wi-Fi",
        "description": "High-speed wireless internet access available in all rooms and public areas."
    },
    {
        "name": "Restaurant",
        "description": "On-site restaurant offering delicious meals and breakfast options."
    },
    {
        "name": "Parking",
        "description": "Free and secure on-site parking for all guests."
    },
    {
        "name": "Room Service",
        "description": "In-room food, beverage, and housekeeping assistance."
    },
    {
        "name": "AC Rooms",
        "description": "Fully air-conditioned rooms for maximum comfort."
    },
    {
        "name": "Swimming Pool",
        "description": "Clean outdoor swimming pool facility available for guests."
    },
    {
        "name": "24/7 Security",
        "description": "Round-the-clock security monitoring and staff to ensure safety."
    }
]


def get_hotel_facilities_info():
    """
    Returns a formatted string containing all official hotel facilities and services
    for inclusion in the AI Concierge prompt context.
    """
    facilities_list = ["Hotel Facilities & Services:"]
    for facility in HOTEL_FACILITIES:
        facilities_list.append(f"- {facility['name']}: {facility['description']}")
    return "\n".join(facilities_list)
