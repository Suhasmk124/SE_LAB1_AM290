"""Decision outcomes and exact boundaries, including short-circuit inputs."""
import pytest
from self_storage import rent_due, access_allowed, payment_status


@pytest.mark.parametrize('size,months,climate,member,expected', [
    ('small', 0, False, False, 0),
    ('small', 1, False, False, 0),
    ('small', 2, False, False, 80),
    ('small', 2, True, True, 0),
    ('small', 3, True, True, 120),
    ('medium', 2, False, False, 0),
    ('medium', 3, False, True, 0),
    ('medium', 4, False, True, 80),
    ('large', 4, False, True, 80),
    ('large', 9, True, False, 720),
    ('large', 10, True, False, 735),
    ('large', 9, False, False, 480),
    ('large', 10, False, False, 490),
])
def test_rent_boundaries(size, months, climate, member, expected):
    assert rent_due(size, months, climate, member) == expected


@pytest.mark.parametrize('size,months,message', [
    ('huge', 1, 'unknown unit size'), ('small', -1, 'invalid months'),
])
def test_invalid_rent(size, months, message):
    with pytest.raises(ValueError, match=message):
        rent_due(size, months, False, False)


@pytest.mark.parametrize('hour,visitors,owner,expected', [
    (0, 4, True, True), (23, 5, True, False),
    (5, 0, False, False), (6, 2, False, True),
    (22, 2, False, True), (23, 0, False, False),
    (12, 3, False, False),
])
def test_access_boundaries(hour, visitors, owner, expected):
    assert access_allowed(hour, visitors, owner) is expected


@pytest.mark.parametrize('autopay,prior,cutoff', [
    (True, False, 0), (False, False, 5),
    (True, True, 10), (False, True, 15),
])
@pytest.mark.parametrize('offset,expected', [
    (0, 'current'), (1, 'current'), (-1, 'grace'),
    (-15, 'grace'), (-16, 'lien'),
])
def test_payment_boundaries(autopay, prior, cutoff, offset, expected):
    assert payment_status(cutoff + offset, autopay, prior) == expected
