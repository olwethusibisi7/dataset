from geopy.geocoders import Nominatim


def geocode_address(address: str, user_agent: str = "isazi_app"):
    """Return (latitude, longitude) for the given address using Nominatim (OpenStreetMap).

    This function is a small example; for production use you should cache results
    and respect Nominatim usage policy (rate limits, identification).
    """
    geolocator = Nominatim(user_agent=user_agent)
    location = geolocator.geocode(address, timeout=10)
    if not location:
        return None
    return (location.latitude, location.longitude)


def main():
    addr = "1600 Pennsylvania Ave NW, Washington, DC"
    coords = geocode_address(addr)
    print(f"Address: {addr}\nCoords: {coords}")


if __name__ == "__main__":
    main()
