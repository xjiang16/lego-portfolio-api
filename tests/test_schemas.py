import pytest
from pydantic import ValidationError

from schemas import LegoSet

VALID_SET = {
    "set_name": "Tiny Plants",
    "set_number": "10329",
    "theme": "Botanicals",
    "purchase_price": 49.99,
    "quantity": 1,
    "estimated_market_value": 49.99,
    "condition": "New",
    "is_sealed": True,
    "notes": "",
}


def test_valid_payload_parses():
    lego_set = LegoSet(**VALID_SET)
    assert lego_set.set_number == "10329"
    assert lego_set.year is None


def test_optional_fields_default_to_none():
    lego_set = LegoSet(**VALID_SET)
    assert lego_set.num_parts is None
    assert lego_set.image_url is None


@pytest.mark.parametrize("missing_field", ["set_name", "set_number", "purchase_price", "quantity"])
def test_missing_required_field_raises(missing_field):
    payload = {k: v for k, v in VALID_SET.items() if k != missing_field}
    with pytest.raises(ValidationError):
        LegoSet(**payload)


@pytest.mark.parametrize("purchase_price", [0, -49.99])
def test_non_positive_purchase_price_raises(purchase_price):
    with pytest.raises(ValidationError):
        LegoSet(**{**VALID_SET, "purchase_price": purchase_price})


@pytest.mark.parametrize("quantity", [0, -1])
def test_non_positive_quantity_raises(quantity):
    with pytest.raises(ValidationError):
        LegoSet(**{**VALID_SET, "quantity": quantity})
