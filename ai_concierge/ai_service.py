# from django.conf import settings
# import google.generativeai as genai

# # Configure Gemini client with API key
# genai.configure(api_key=settings.GEMINI_API_KEY)

# # Initialize the model
# model = genai.GenerativeModel('gemini-3.6-flash')



#     rooms = Room.objects.filter(
#         available=True
#     ).order_by("price")

#     if not rooms.exists():
#         return "Currently, no rooms are available."

#     room_information = []

#     for room in rooms:

#         room_information.append(
#             f"""
# Room Number: {room.room_number}
# Room Type: {room.room_type}
# Price: ₹{room.price}
# Capacity: {room.capacity} guests
# Description: {room.description}
# """
#         )

#     return "\n".join(room_information)


# def get_customer_bookings(user):

#     if not user or not user.is_authenticated:
#         return "Customer is not logged in."

#     bookings = Booking.objects.filter(
#         user=user
#     ).select_related("room").order_by("-booking_date")

#     if not bookings.exists():
#         return "No booking found for this customer."

#     booking_information = []

#     for booking in bookings:
#         stay_duration = (booking.check_out - booking.check_in).days

#         payments = booking.payments.all()
#         payment_str = ""
#         if payments.exists():
#             for p in payments:
#                 payment_str += f"\n  - Receipt: {p.receipt_number} | Amount: ₹{p.amount} | Status: {p.status} | Method: {p.payment_method}"
#         else:
#             payment_str = "\n  - No payment records found."

#         booking_information.append(
#             f"""
# Booking ID: {booking.id}
# Room Number: {booking.room.room_number}
# Room Type: {booking.room.room_type}
# Check-in: {booking.check_in}
# Check-out: {booking.check_out}
# Stay Duration: {stay_duration} days
# Adults: {booking.adults}
# Children: {booking.children}
# Booking Date: {booking.booking_date}
# Booking Status: {booking.status}
# Payment Information:{payment_str}
# """
#         )

#     return "\n".join(booking_information)


# # =====================================================
# # Recommend Rooms Based On Number Of Guests
# # =====================================================

# def get_recommended_rooms(adults, children):

#     total_guests = adults + children

#     rooms = Room.objects.filter(
#         available=True,
#         capacity__gte=total_guests
#     ).order_by("price")

#     if not rooms.exists():
#         return f"No available room found for {total_guests} guests."

#     room_information = []

#     for room in rooms:

#         room_information.append(
#             f"""
# Room Number: {room.room_number}
# Room Type: {room.room_type}
# Price: ₹{room.price} per night
# Capacity: {room.capacity} guests
# Description: {room.description}
# """
#         )

#     return "\n".join(room_information)


# # =====================================================
# # Budget-Based Room Recommendation
# # =====================================================

# def get_budget_rooms(budget):

#     rooms = Room.objects.filter(
#         available=True,
#         price__lte=budget
#     ).order_by("price")

#     if not rooms.exists():
#         return f"No available room found within a budget of Rs.{budget}."

#     room_information = []

#     for room in rooms:
#         room_information.append(
#             f"""
# Room Number: {room.room_number}
# Room Type: {room.room_type}
# Price: Rs.{room.price} per night
# Capacity: {room.capacity} guests
# Description: {room.description}
# """
#         )

#     return "\n".join(room_information)


# # --------------------------------------------------------
# # Robust guest count parser - handles many sentence formats
# # --------------------------------------------------------

# def parse_guest_count(message):
#     """
#     Safely parse a natural language message to extract the number of adults and children.
#     Supports various phrasings such as:
#         - "2 adults"
#         - "4 adults and 2 children/kids"
#         - "2 adults, 2 kids"
#         - "adults: 2 children: 2"
#         - "family of 5"
#         - "we are 4 adults and 2 kids"
#         - "room for 3"
#         - "6 guests"
#     Returns a tuple (adults, children) where missing values default to 0.
#     If the message cannot be interpreted, returns (None, None).
#     """
#     msg = message.lower()

#     # Helper to ensure non-negative integers
#     def safe_int(value):
#         try:
#             iv = int(value)
#             return iv if iv >= 0 else None
#         except Exception:
#             return None

#     # Pattern 1: "X adults and Y children/kids" with optional connectors (and, &, ,, +)
#     m = re.search(r"(\d+)\s*adults?\s*(?:and|&|,|\+)?\s*(\d+)\s*(?:children|child|kids?)", msg)
#     if m:
#         adults = safe_int(m.group(1))
#         children = safe_int(m.group(2))
#         if adults is not None and children is not None:
#             return adults, children

#     # Pattern 1b: "X adults Y children" (no connector)
#     m = re.search(r"(\d+)\s*adults?\s+(\d+)\s*(?:children|child|kids?)", msg)
#     if m:
#         adults = safe_int(m.group(1))
#         children = safe_int(m.group(2))
#         if adults is not None and children is not None:
#             return adults, children

#     # Pattern 2: "adults: X children: Y" or "adults X children Y"
#     m = re.search(r"adults?[:\s]+(\d+)[^\d]+children?[:\s]+(\d+)", msg)
#     if m:
#         adults = safe_int(m.group(1))
#         children = safe_int(m.group(2))
#         if adults is not None and children is not None:
#             return adults, children

#     # Pattern 3: "X adults" only
#     m = re.search(r"(\d+)\s*adults?", msg)
#     if m:
#         adults = safe_int(m.group(1))
#         if adults is not None:
#             return adults, 0

#     # Pattern 4: "X guests / people / persons / pax"
#     m = re.search(r"(\d+)\s*(?:guests?|people|persons?|pax)", msg)
#     if m:
#         total = safe_int(m.group(1))
#         if total is not None:
#             return total, 0

#     # Pattern 5: "family of X"
#     m = re.search(r"family\s+of\s+(\d+)", msg)
#     if m:
#         total = safe_int(m.group(1))
#         if total is not None:
#             return total, 0

#     # Pattern 6: "room for X" / "stay for X" / "accommodate X"
#     if any(kw in msg for kw in ['room for', 'stay for', 'booking for', 'accommodate']):
#         m = re.search(r"for\s+(\d+)", msg)
#         if m:
#             total = safe_int(m.group(1))
#             if total is not None:
#                 return total, 0

#     return None, None


# def ask_ai_concierge(user_message, user=None):

#     # -----------------------------------------
#     # Get real room data from database
#     # -----------------------------------------

#     available_rooms = get_available_rooms()

#     customer_bookings = get_customer_bookings(user)

#     hotel_facilities = get_hotel_facilities_info()

#     # -----------------------------------------
#     # Detect guest count from customer message
#     # -----------------------------------------

#     # Initialize recommendation and budget placeholders
#     # Determine recommendation based on parsed guest count
#     recommended_rooms = ""
#     budget_rooms = ""
#     adults, children = parse_guest_count(user_message)
#     if adults is not None:
#         # Ensure children is an integer (default 0)
#         children = children if children is not None else 0
#         recommended_rooms = get_recommended_rooms(adults, children)
#     else:
#         # Prompt user for clarification when guest count cannot be determined
#         recommended_rooms = "Could you please let me know the number of adults and children for your stay?"

#     # -----------------------------------------
#     # Detect budget from customer message
#     # -----------------------------------------

#     budget_match = re.search(
#         r'(?:under|below|less\s+than|within|budget\s+of|upto|up\s+to)?\s*[\u20b9rs\.]*\s*(\d+(?:,\d+)*(?:\.\d+)?)',
#         user_message.lower()
#     )

#     if budget_match and any(kw in user_message.lower() for kw in [
#         'under', 'below', 'budget', 'cheap', 'affordable', 'less than',
#         'within', 'upto', 'up to', 'price', 'cost', 'inexpensive'
#     ]):
#         budget_value = float(budget_match.group(1).replace(',', ''))
#         budget_rooms = get_budget_rooms(budget_value)

#     # -----------------------------------------
#     # System Prompt
#     # -----------------------------------------

#     system_prompt = f"""
# You are Smart Hotel AI Concierge.

# You are an AI assistant for Smart Hotel Management System.

# Your job is to help hotel customers with:

# 1. Room information
# 2. Hotel facilities
# 3. Booking guidance
# 4. Payment guidance
# 5. Check-in and check-out information
# 6. Cancellation guidance
# 7. Hotel policies
# 8. General hotel-related questions

# Hotel Information:

# Hotel Name:
# Smart Hotel

# Location:
# Ahmedabad, Gujarat, India

# Phone:
# +91 9876543210

# Email:
# smarthotel@gmail.com

# Check-in:
# 2:00 PM

# Check-out:
# 11:00 AM


# ==================================================
# HOTEL FACILITIES & SERVICES KNOWLEDGE
# ==================================================

# {hotel_facilities}


# ==================================================
# REAL ROOM INFORMATION
# ==================================================

# {available_rooms}


# ==================================================
# CUSTOMER'S REAL BOOKING INFORMATION
# ==================================================

# {customer_bookings}


# ==================================================
# ROOM RECOMMENDATION INFORMATION
# ==================================================

# {recommended_rooms}


# ==================================================
# BUDGET-BASED ROOM RECOMMENDATIONS
# ==================================================

# {budget_rooms}


# FACILITY RULES:

# - Use the HOTEL FACILITIES & SERVICES KNOWLEDGE provided above to answer any questions regarding facilities, amenities, or services.
# - Do not invent facilities or services. Only state that the hotel provides a facility if it is listed in the HOTEL FACILITIES & SERVICES KNOWLEDGE.
# - If a guest asks about a facility or service that is NOT listed (e.g., Gym, Spa, Airport Shuttle, Pet-friendly, Valet Parking, etc.), state clearly and politely that the hotel does not provide that facility or service.
# - If a guest asks general questions like "What facilities does the hotel provide?", list the facilities from the knowledge base above clearly.

# ROOM RULES:

# - Use the room information provided above.
# - Do not invent room numbers.
# - Do not invent room types.
# - Do not invent room prices.
# - Do not invent room capacity.
# - Only recommend currently available rooms.
# - Never recommend a room whose capacity is lower than the total number of guests.
# - If no suitable room is available, clearly tell the customer.
# - If the customer has not provided the number of guests, ask how many adults and children will stay.

# BUDGET RULES:

# - Use the BUDGET-BASED ROOM RECOMMENDATIONS section to answer budget-related questions.
# - If a customer asks for rooms "under", "below", "within", "less than" a certain price, or asks for "cheap", "affordable", or "cheapest" rooms, use the BUDGET-BASED ROOM RECOMMENDATIONS data above.
# - Never invent prices. Only show rooms and prices from the database.
# - Present budget room results sorted from cheapest to most expensive.
# - If no rooms are available within the customer's budget, clearly say so and suggest they contact the hotel staff for special pricing or alternative options.
# - If the customer asks "Show me the cheapest available room", present the first (lowest-priced) room from the REAL ROOM INFORMATION.

# BOOKING RULES:

# - The CUSTOMER'S REAL BOOKING INFORMATION belongs to the currently logged-in customer.
# - Use this information when the customer asks about their booking.
# - Never invent booking details.
# - Never invent a booking status. The only valid statuses in the system are: Pending, Approved, Confirmed, Cancelled, Rejected.
# - You must use the actual booking status exactly as provided from the database.
# - If a customer asks "What is the status of my booking?", answer in this exact format: "Your booking #[ID] for Room [Room Number] is currently [Status]." (e.g., "Your booking #23 for Room 514 is currently Approved.").
# - Do not claim that a booking is confirmed unless the database says it is confirmed.
# - Do not make a reservation yourself.
# - If the customer wants to book a room, guide them to the Booking section.

# SECURITY RULE:

# - Only use booking information belonging to the currently logged-in user.
# - Never show another customer's booking.
# - Never reveal information about another customer.
# - Never expose another customer's name, room, dates or payment information.

# POLICY RULES:

# - Use the Hotel Information (Check-in: 2:00 PM, Check-out: 11:00 AM) to answer time-related questions.
# - Do not invent or hallucinate policies for late arrivals, check-in document requirements, or booking modifications.
# - If a guest asks about a policy that is not explicitly defined in the provided context (e.g., "What happens if I arrive late?", "Can I modify my booking?", "What documents are required during check-in?"), clearly state that they should contact the hotel staff or admin directly at smarthotel@gmail.com or +91 9876543210 for assistance.

# CANCELLATION GUIDANCE RULES:

# - If a customer asks "Can I cancel my booking?", "How can I cancel my booking?", "Which booking can I cancel?", or any similar question, follow these rules:
#   1. The AI must NOT cancel any booking directly. Booking cancellations are handled by hotel staff.
#   2. Guide the customer to visit the "My Bookings" section of the website, where they can view their bookings and request changes through the hotel.
#   3. You may also tell the customer to contact hotel staff directly: Email smarthotel@gmail.com or call +91 9876543210.
# - If the customer asks "What is my cancellation policy?", explain that the hotel manages cancellations on a case-by-case basis. Direct them to contact the hotel staff for specific cancellation terms via smarthotel@gmail.com or +91 9876543210.
# - If the customer asks "Which booking can I cancel?", show them their current active bookings (those with status Pending or Approved) from their CUSTOMER'S REAL BOOKING INFORMATION, and then instruct them to contact hotel staff to proceed with the cancellation.
# - Never change the booking status to Cancelled yourself.
# - A booking with status "Cancelled" or "Rejected" cannot be cancelled again.

# BOOKING DATE RULES:

# - When a customer asks "When is my check-in?", respond with the Check-in date from their booking.
# - When a customer asks "When do I check out?", respond with the Check-out date from their booking.
# - When a customer asks "How many days is my stay?" or "What is the duration of my stay?", use the "Stay Duration" field already calculated in their booking data.
# - When a customer asks "What room am I staying in?", respond with the Room Number and Room Type from their booking.
# - Never invent or calculate dates yourself. Always use the values provided in the CUSTOMER'S REAL BOOKING INFORMATION.

# PAYMENT RULES:

# - Payment methods accepted by the hotel are: Cash, UPI, Credit Card, Debit Card, Net Banking.
# - If a customer asks about payment methods, list the above accepted methods.
# - When a customer asks "What is the payment status of my booking?", use the Payment Information from their booking data to respond. Report the Receipt Number, Amount, Status, and Payment Method.
# - The only valid payment statuses in the system are: Pending, Paid, Failed, Refunded.
# - Never invent a payment status.
# - Never expose card numbers, CVV, passwords, or any sensitive payment credentials.
# - Only show the payment information of the currently logged-in customer. Never reveal another customer's payment data.
# - If payment information is not available in the provided booking data, tell the customer to visit the Payment section of the website for details.

# BOOKING SUMMARY RULES:

# - If a customer asks "Show me my booking summary", "Give me my hotel stay details", "Summarize my booking", or any similar request, respond with a professional formatted summary using ONLY the data provided in the CUSTOMER'S REAL BOOKING INFORMATION.
# - For each booking, include ALL of the following fields in the summary:
#   1. Booking ID
#   2. Room Number
#   3. Room Type
#   4. Check-in Date
#   5. Check-out Date
#   6. Stay Duration (in days)
#   7. Number of Adults
#   8. Number of Children
#   9. Booking Status
# - If the customer has multiple bookings, display each booking as a separate section clearly labeled (e.g., "Booking #23", "Booking #22").
# - Never invent or omit any field from the summary.
# - Never include another customer's booking in the summary.
# - Present the summary in a clear, professional, easy-to-read format.
# """

#     # -----------------------------------------
#     # Send request to Gemini
#     # -----------------------------------------

#     try:
#         response = model.generate_content(
#             system_instruction=system_prompt,
#             contents=user_message,
#         )
#         return response.text
#     except Exception as e:
#         error_str = str(e)
#         if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
#             return "I'm sorry, the AI assistant is temporarily unavailable due to high demand. Please try again in a few minutes, or contact hotel staff at smarthotel@gmail.com or +91 9876543210 for immediate assistance."
#         return "I'm sorry, I encountered an unexpected error. Please try again or contact hotel staff at smarthotel@gmail.com or +91 9876543210 for assistance."





import re

from django.conf import settings
import google.generativeai as genai

from rooms.models import Room
from booking.models import Booking
from .facilities import get_hotel_facilities_info


# =====================================================
# Configure Gemini Client
# =====================================================

genai.configure(
    api_key=settings.GEMINI_API_KEY
)


# =====================================================
# Initialize Gemini Model
# =====================================================

model = genai.GenerativeModel(
    "gemini-3.6-flash"
)


# =====================================================
# Get Available Rooms
# =====================================================

def get_available_rooms():

    rooms = Room.objects.filter(
        available=True
    ).order_by("price")

    if not rooms.exists():
        return "Currently, no rooms are available."

    room_information = []

    for room in rooms:

        room_information.append(
            f"""
Room Number: {room.room_number}
Room Type: {room.room_type}
Price: ₹{room.price}
Capacity: {room.capacity} guests
Description: {room.description}
"""
        )

    return "\n".join(room_information)


# =====================================================
# Get Customer Bookings
# =====================================================

def get_customer_bookings(user):

    if not user or not user.is_authenticated:
        return "Customer is not logged in."

    bookings = (
        Booking.objects
        .filter(user=user)
        .select_related("room")
        .order_by("-booking_date")
    )

    if not bookings.exists():
        return "No booking found for this customer."

    booking_information = []

    for booking in bookings:

        stay_duration = (
            booking.check_out - booking.check_in
        ).days

        # ---------------------------------------------
        # Get payment information
        # ---------------------------------------------

        payments = booking.payments.all()

        payment_str = ""

        if payments.exists():

            for payment in payments:

                payment_str += (
                    f"\n  - Receipt: {payment.receipt_number}"
                    f" | Amount: ₹{payment.amount}"
                    f" | Status: {payment.status}"
                    f" | Method: {payment.payment_method}"
                )

        else:

            payment_str = (
                "\n  - No payment records found."
            )

        # ---------------------------------------------
        # Booking information
        # ---------------------------------------------

        booking_information.append(
            f"""
Booking ID: {booking.id}
Room Number: {booking.room.room_number}
Room Type: {booking.room.room_type}
Check-in: {booking.check_in}
Check-out: {booking.check_out}
Stay Duration: {stay_duration} days
Adults: {booking.adults}
Children: {booking.children}
Booking Date: {booking.booking_date}
Booking Status: {booking.status}
Payment Information:{payment_str}
"""
        )

    return "\n".join(booking_information)


# =====================================================
# Recommend Rooms Based On Number Of Guests
# =====================================================

def get_recommended_rooms(adults, children):

    total_guests = adults + children

    rooms = Room.objects.filter(
        available=True,
        capacity__gte=total_guests
    ).order_by("price")

    if not rooms.exists():

        return (
            f"No available room found for "
            f"{total_guests} guests."
        )

    room_information = []

    for room in rooms:

        room_information.append(
            f"""
Room Number: {room.room_number}
Room Type: {room.room_type}
Price: ₹{room.price} per night
Capacity: {room.capacity} guests
Description: {room.description}
"""
        )

    return "\n".join(room_information)


# =====================================================
# Budget-Based Room Recommendation
# =====================================================

def get_budget_rooms(budget):

    rooms = Room.objects.filter(
        available=True,
        price__lte=budget
    ).order_by("price")

    if not rooms.exists():

        return (
            f"No available room found within "
            f"a budget of Rs.{budget}."
        )

    room_information = []

    for room in rooms:

        room_information.append(
            f"""
Room Number: {room.room_number}
Room Type: {room.room_type}
Price: Rs.{room.price} per night
Capacity: {room.capacity} guests
Description: {room.description}
"""
        )

    return "\n".join(room_information)


# =====================================================
# Robust Guest Count Parser
# =====================================================

def parse_guest_count(message):
    """
    Safely parse a natural language message to extract
    the number of adults and children.

    Supports:
        - "2 adults"
        - "4 adults and 2 children"
        - "2 adults, 2 kids"
        - "adults: 2 children: 2"
        - "family of 5"
        - "we are 4 adults and 2 kids"
        - "room for 3"
        - "6 guests"

    Returns:
        (adults, children)

    If the message cannot be interpreted:
        (None, None)
    """

    msg = message.lower()

    # =================================================
    # Helper Function
    # =================================================

    def safe_int(value):

        try:

            iv = int(value)

            return (
                iv
                if iv >= 0
                else None
            )

        except Exception:

            return None

    # =================================================
    # Pattern 1
    # "X adults and Y children/kids"
    # =================================================

    m = re.search(
        r"(\d+)\s*adults?\s*"
        r"(?:and|&|,|\+)?\s*"
        r"(\d+)\s*"
        r"(?:children|child|kids?)",
        msg
    )

    if m:

        adults = safe_int(
            m.group(1)
        )

        children = safe_int(
            m.group(2)
        )

        if (
            adults is not None
            and children is not None
        ):

            return adults, children

    # =================================================
    # Pattern 1b
    # "X adults Y children"
    # =================================================

    m = re.search(
        r"(\d+)\s*adults?\s+"
        r"(\d+)\s*"
        r"(?:children|child|kids?)",
        msg
    )

    if m:

        adults = safe_int(
            m.group(1)
        )

        children = safe_int(
            m.group(2)
        )

        if (
            adults is not None
            and children is not None
        ):

            return adults, children

    # =================================================
    # Pattern 2
    # "adults: X children: Y"
    # =================================================

    m = re.search(
        r"adults?[:\s]+(\d+)"
        r"[^\d]+"
        r"children?[:\s]+(\d+)",
        msg
    )

    if m:

        adults = safe_int(
            m.group(1)
        )

        children = safe_int(
            m.group(2)
        )

        if (
            adults is not None
            and children is not None
        ):

            return adults, children

    # =================================================
    # Pattern 3
    # "X adults"
    # =================================================

    m = re.search(
        r"(\d+)\s*adults?",
        msg
    )

    if m:

        adults = safe_int(
            m.group(1)
        )

        if adults is not None:

            return adults, 0

    # =================================================
    # Pattern 4
    # "X guests / people / persons / pax"
    # =================================================

    m = re.search(
        r"(\d+)\s*"
        r"(?:guests?|people|persons?|pax)",
        msg
    )

    if m:

        total = safe_int(
            m.group(1)
        )

        if total is not None:

            return total, 0

    # =================================================
    # Pattern 5
    # "family of X"
    # =================================================

    m = re.search(
        r"family\s+of\s+(\d+)",
        msg
    )

    if m:

        total = safe_int(
            m.group(1)
        )

        if total is not None:

            return total, 0

    # =================================================
    # Pattern 6
    # "room for X"
    # "stay for X"
    # "booking for X"
    # "accommodate X"
    # =================================================

    if any(
        keyword in msg
        for keyword in [
            "room for",
            "stay for",
            "booking for",
            "accommodate"
        ]
    ):

        m = re.search(
            r"for\s+(\d+)",
            msg
        )

        if m:

            total = safe_int(
                m.group(1)
            )

            if total is not None:

                return total, 0

    # =================================================
    # No guest count detected
    # =================================================

    return None, None


# =====================================================
# AI Concierge
# =====================================================

def ask_ai_concierge(
    user_message,
    user=None
):

    # =================================================
    # Get Real Room Data
    # =================================================

    available_rooms = (
        get_available_rooms()
    )

    customer_bookings = (
        get_customer_bookings(user)
    )

    hotel_facilities = (
        get_hotel_facilities_info()
    )

    # =================================================
    # Detect Guest Count
    # =================================================

    recommended_rooms = ""

    budget_rooms = ""

    adults, children = (
        parse_guest_count(
            user_message
        )
    )

    if adults is not None:

        children = (
            children
            if children is not None
            else 0
        )

        recommended_rooms = (
            get_recommended_rooms(
                adults,
                children
            )
        )

    else:

        recommended_rooms = (
            "Could you please let me know "
            "the number of adults and children "
            "for your stay?"
        )

    # =================================================
    # Detect Budget
    # =================================================

    budget_match = re.search(
        r"(?:under|below|less\s+than|within|"
        r"budget\s+of|upto|up\s+to)?\s*"
        r"[\u20b9rs\.]*\s*"
        r"(\d+(?:,\d+)*(?:\.\d+)?)",
        user_message.lower()
    )

    if (
        budget_match
        and any(
            keyword in user_message.lower()
            for keyword in [
                "under",
                "below",
                "budget",
                "cheap",
                "affordable",
                "less than",
                "within",
                "upto",
                "up to",
                "price",
                "cost",
                "inexpensive"
            ]
        )
    ):

        budget_value = float(
            budget_match
            .group(1)
            .replace(",", "")
        )

        budget_rooms = (
            get_budget_rooms(
                budget_value
            )
        )

    # =================================================
    # System Prompt
    # =================================================

    system_prompt = f"""
You are Smart Hotel AI Concierge.

You are an AI assistant for Smart Hotel Management System.

Your job is to help hotel customers with:

1. Room information
2. Hotel facilities
3. Booking guidance
4. Payment guidance
5. Check-in and check-out information
6. Cancellation guidance
7. Hotel policies
8. General hotel-related questions


==================================================
HOTEL INFORMATION
==================================================

Hotel Name:
Smart Hotel

Location:
Ahmedabad, Gujarat, India

Phone:
+91 9876543210

Email:
smarthotel@gmail.com

Check-in:
2:00 PM

Check-out:
11:00 AM


==================================================
HOTEL FACILITIES & SERVICES KNOWLEDGE
==================================================

{hotel_facilities}


==================================================
REAL ROOM INFORMATION
==================================================

{available_rooms}


==================================================
CUSTOMER'S REAL BOOKING INFORMATION
==================================================

{customer_bookings}


==================================================
ROOM RECOMMENDATION INFORMATION
==================================================

{recommended_rooms}


==================================================
BUDGET-BASED ROOM RECOMMENDATIONS
==================================================

{budget_rooms}


==================================================
FACILITY RULES
==================================================

- Use the HOTEL FACILITIES & SERVICES KNOWLEDGE
  provided above to answer questions regarding
  facilities, amenities, or services.

- Do not invent facilities or services.

- Only state that the hotel provides a facility
  if it is listed in the HOTEL FACILITIES &
  SERVICES KNOWLEDGE.

- If a guest asks about a facility or service
  that is NOT listed, clearly and politely state
  that the hotel does not provide that facility
  or service.

- If a guest asks general questions such as
  "What facilities does the hotel provide?",
  list the facilities from the knowledge base.


==================================================
ROOM RULES
==================================================

- Use the room information provided above.

- Do not invent room numbers.

- Do not invent room types.

- Do not invent room prices.

- Do not invent room capacity.

- Only recommend currently available rooms.

- Never recommend a room whose capacity is lower
  than the total number of guests.

- If no suitable room is available, clearly tell
  the customer.

- If the customer has not provided the number of
  guests, ask how many adults and children will stay.


==================================================
BUDGET RULES
==================================================

- Use the BUDGET-BASED ROOM RECOMMENDATIONS section
  for budget-related questions.

- If a customer asks for rooms "under", "below",
  "within", or "less than" a certain price, or asks
  for "cheap", "affordable", or "cheapest" rooms,
  use the budget recommendation data.

- Never invent prices.

- Only show rooms and prices from the database.

- Present budget room results sorted from cheapest
  to most expensive.

- If no rooms are available within the customer's
  budget, clearly say so and suggest contacting
  hotel staff for special pricing or alternatives.

- If the customer asks:
  "Show me the cheapest available room",
  present the first lowest-priced room from the
  REAL ROOM INFORMATION.


==================================================
BOOKING RULES
==================================================

- The CUSTOMER'S REAL BOOKING INFORMATION belongs
  to the currently logged-in customer.

- Use this information when the customer asks
  about their booking.

- Never invent booking details.

- Never invent a booking status.

- The only valid booking statuses are:

  Pending
  Approved
  Confirmed
  Cancelled
  Rejected

- You must use the actual booking status exactly
  as provided from the database.

- If a customer asks:
  "What is the status of my booking?"

  Answer in this format:

  "Your booking #[ID] for Room [Room Number]
   is currently [Status]."

- Do not claim that a booking is confirmed unless
  the database says it is confirmed.

- Do not make a reservation yourself.

- If the customer wants to book a room, guide them
  to the Booking section.


==================================================
SECURITY RULE
==================================================

- Only use booking information belonging to the
  currently logged-in user.

- Never show another customer's booking.

- Never reveal information about another customer.

- Never expose another customer's name, room,
  dates, or payment information.


==================================================
POLICY RULES
==================================================

- Use the Hotel Information for check-in and
  check-out time questions.

- Check-in:
  2:00 PM

- Check-out:
  11:00 AM

- Do not invent policies for late arrivals,
  check-in document requirements, or booking
  modifications.

- If a guest asks about a policy that is not
  explicitly defined in the provided context,
  tell them to contact hotel staff or admin.

Hotel Email:
smarthotel@gmail.com

Hotel Phone:
+91 9876543210


==================================================
CANCELLATION GUIDANCE RULES
==================================================

- The AI must NOT cancel any booking directly.

- Booking cancellations are handled by hotel staff.

- Guide the customer to visit the "My Bookings"
  section of the website.

- Customers may also contact hotel staff:

  Email:
  smarthotel@gmail.com

  Phone:
  +91 9876543210

- If the customer asks:
  "What is my cancellation policy?"

  Explain that the hotel manages cancellations
  on a case-by-case basis.

- If the customer asks:
  "Which booking can I cancel?"

  Show their current active bookings with status
  Pending or Approved.

- Never change the booking status to Cancelled.

- A booking with status Cancelled or Rejected
  cannot be cancelled again.


==================================================
BOOKING DATE RULES
==================================================

- When a customer asks:
  "When is my check-in?"

  Respond with the Check-in date from their booking.

- When a customer asks:
  "When do I check out?"

  Respond with the Check-out date from their booking.

- When a customer asks:
  "How many days is my stay?"

  Use the Stay Duration field already calculated
  in the booking data.

- When a customer asks:
  "What room am I staying in?"

  Respond with the Room Number and Room Type.

- Never invent dates.

- Always use values provided in the
  CUSTOMER'S REAL BOOKING INFORMATION.


==================================================
PAYMENT RULES
==================================================

Accepted payment methods:

- Cash
- UPI
- Credit Card
- Debit Card
- Net Banking

- If a customer asks about payment methods,
  list the accepted payment methods.

- If a customer asks:
  "What is the payment status of my booking?"

  Use the Payment Information from their booking.

- Report:

  Receipt Number
  Amount
  Status
  Payment Method

- The only valid payment statuses are:

  Pending
  Paid
  Failed
  Refunded

- Never invent a payment status.

- Never expose card numbers, CVV, passwords,
  or other sensitive payment credentials.

- Only show payment information belonging to
  the currently logged-in customer.

- If payment information is not available,
  tell the customer to visit the Payment section.


==================================================
BOOKING SUMMARY RULES
==================================================

- If a customer asks:
  "Show me my booking summary",
  "Give me my hotel stay details",
  "Summarize my booking",

  provide a professional formatted summary.

- Use ONLY the data provided in the
  CUSTOMER'S REAL BOOKING INFORMATION.

- For each booking include:

  1. Booking ID
  2. Room Number
  3. Room Type
  4. Check-in Date
  5. Check-out Date
  6. Stay Duration
  7. Number of Adults
  8. Number of Children
  9. Booking Status

- If there are multiple bookings,
  display each booking as a separate section.

- Never invent information.

- Never omit required booking information.

- Never include another customer's booking.

- Present the summary in a clear, professional,
  easy-to-read format.
"""

    # =================================================
    # Send Request To Gemini
    # =================================================

    try:

        response = model.generate_content(
            contents=user_message,
            generation_config={
                "system_instruction": system_prompt
            }
        )

        return response.text

    except Exception as e:

        error_str = str(e)

        # ---------------------------------------------
        # Gemini rate limit / high demand
        # ---------------------------------------------

        if (
            "RESOURCE_EXHAUSTED" in error_str
            or "429" in error_str
        ):

            return (
                "I'm sorry, the AI assistant is "
                "temporarily unavailable due to high "
                "demand. Please try again in a few "
                "minutes, or contact hotel staff at "
                "smarthotel@gmail.com or "
                "+91 9876543210 for immediate assistance."
            )

        # ---------------------------------------------
        # General error
        # ---------------------------------------------

        return (
            "I'm sorry, I encountered an unexpected "
            "error. Please try again or contact hotel "
            "staff at smarthotel@gmail.com or "
            "+91 9876543210 for assistance."
        )
