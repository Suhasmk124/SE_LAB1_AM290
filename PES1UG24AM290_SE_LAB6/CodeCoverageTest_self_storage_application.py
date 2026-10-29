"""Line coverage: execute every statement, including validation failures."""
import pytest
from self_storage import rent_due, access_allowed, payment_status


@pytest.mark.parametrize('size,months,climate,member,expected', [
    ('small', 1, False, False, 0),
    ('medium', 4, False, True, 80),
    ('large', 10, True, False, 735),
])
def test_rent(size, months, climate, member, expected):
    assert rent_due(size, months, climate, member) == expected


def test_invalid_size():
    with pytest.raises(ValueError, match='unknown unit size'):
        rent_due('huge', 2, False, False)


def test_negative_months():
    with pytest.raises(ValueError, match='invalid months'):
        rent_due('small', -1, False, False)


@pytest.mark.parametrize('hour,visitors,owner,expected', [
    (0, 4, True, True), (5, 1, False, False), (12, 2, False, True),
])
def test_access(hour, visitors, owner, expected):
    assert access_allowed(hour, visitors, owner) is expected


@pytest.mark.parametrize('days,autopay,prior,expected', [
    (0, True, False, 'current'), (0, False, True, 'grace'),
    (-16, True, False, 'lien'),
])
def test_payment(days, autopay, prior, expected):
    assert payment_status(days, autopay, prior) == expected
