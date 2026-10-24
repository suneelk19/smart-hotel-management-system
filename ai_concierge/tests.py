from django.test import TestCase
from ai_concierge.facilities import HOTEL_FACILITIES, get_hotel_facilities_info
from ai_concierge.ai_service import get_available_rooms


class FacilitiesTestCase(TestCase):

    def test_facilities_list_contents(self):
        facility_names = [f["name"] for f in HOTEL_FACILITIES]
        expected_facilities = [
            "Free Wi-Fi",
            "Restaurant",
            "Parking",
            "Room Service",
            "AC Rooms",
            "Swimming Pool",
            "24/7 Security",
        ]
        for expected in expected_facilities:
            self.assertIn(expected, facility_names)

    def test_get_hotel_facilities_info(self):
        info = get_hotel_facilities_info()
        self.assertIn("Hotel Facilities & Services:", info)
        self.assertIn("Free Wi-Fi", info)
        self.assertIn("Restaurant", info)
        self.assertIn("Parking", info)
        self.assertIn("Room Service", info)
        self.assertIn("AC Rooms", info)
        self.assertIn("Swimming Pool", info)
        self.assertIn("24/7 Security", info)
