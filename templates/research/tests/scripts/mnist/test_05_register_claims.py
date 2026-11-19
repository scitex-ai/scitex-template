"""scripts/mnist/05_register_claims.py: stated values and locators."""

import pytest
from conftest import load_script


@pytest.fixture(scope="module")
def claims():
    return load_script("05_register_claims")


def test_stated_value_is_an_integer_when_written_without_decimals(claims):
    # Arrange
    raw = 4_999.6
    # Act
    value = claims.stated_value(raw, 0)
    # Assert
    assert value == 5_000 and isinstance(value, int)


def test_stated_value_rounds_to_the_written_precision(claims):
    # Arrange
    raw = 0.961234
    # Act
    value = claims.stated_value(raw, 4)
    # Assert
    assert value == 0.9612


def test_resolve_pointer_walks_nested_dicts_and_lists(claims):
    # Arrange
    doc = {"SVC": {"accuracy": 0.96}, "table": [[1, 2], [3, 4]]}
    # Act
    value = claims.resolve_pointer(doc, "/table/1/0")
    # Assert
    assert value == 3
