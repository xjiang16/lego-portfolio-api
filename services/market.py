import random

def get_market_price(set_number: str):
    """
    Mock Service: Simulates fetching the current 'Sold' price from eBay.
    """
    # Hardcoded 'Real' values for specific sets
    mock_data = {
        "10329": 54.99,  # Tiny Plants (MSRP $49.99)
        "10311": 52.00,  # Orchid (MSRP $49.99)
        "10309": 58.50   # Succulents (MSRP $49.99)
    }

    # If the set isn't in the list, generate a price with 5-15% growth
    if set_number in mock_data:
        return mock_data[set_number]

    return 49.99 * random.uniform(1.05, 1.15)