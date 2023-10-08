from geopy.geocoders import Nominatim

from app.schemas.enums import Languages


def replace_polish_chars(input_string: str) -> str:
    """
    Function to replace Polish characters with English counterparts
    """
    polish_to_english = {
        "ą": "a",
        "ć": "c",
        "ę": "e",
        "ł": "l",
        "ń": "n",
        "ó": "o",
        "ś": "s",
        "ź": "z",
        "ż": "z",
    }
    result = ""
    for char in input_string.lower():
        # Use the dictionary to replace Polish characters
        result += polish_to_english.get(char, char)
    return result


async def get_country_from_city(city_name) -> tuple[str, str]:
    geolocator = Nominatim(user_agent="city_to_country")
    try:
        location = geolocator.geocode(city_name, addressdetails=True, language="en")
        if location and "address" in location.raw:
            address = location.raw["address"]
            country = address.get("country")
            country_abbreviation = address.get("country_code")
            if country:
                return country, country_abbreviation
        else:
            raise ValueError("Country not found")
    except Exception as e:
        raise ValueError(str(e))


async def get_language_enum(language: str) -> "Languages":
    language_mapping = {"English": Languages.ENGLISH, "Ukrainian": Languages.UKRAINIAN, "Polish": Languages.POLISH}

    return language_mapping.get(language)
