from datetime import date
import pytest
from cmm.utils.date import Period, flat_overlap


@pytest.fixture(name='test_period')
def fixture_test_period():
    """period to test"""
    return Period(date(2000, 1, 1), date(2000, 2, 15))
    
def test_swap(test_period):
    """swap start and end"""
    assert test_period == Period(date(2000, 2, 15), date(2000, 1, 1))

def test_overlapped_period(test_period):
    """overlapped"""
    assert flat_overlap([test_period, Period(date(2000, 1, 10), date(2000, 3, 1))]) == \
        [Period(date(2000, 1, 1), date(2000, 1, 9)),
         Period(date(2000, 1, 10), date(2000, 2, 15)),
         Period(date(2000, 2, 16), date(2000, 3, 1))]

def test_overlapped_one_day(test_period):
    """overlapped only one day"""
    assert flat_overlap([test_period, Period(date(2000, 2, 15), date(2000, 3, 1))]) == \
        [Period(date(2000, 1, 1), date(2000, 2, 14)),
         Period(date(2000, 2, 15), date(2000, 2, 15)),
         Period(date(2000, 2, 16), date(2000, 3, 1))]

def test_contains(test_period):
    """one contains another period"""
    assert flat_overlap([test_period, Period(date(2000, 1, 15), date(2000, 2, 1))]) == \
        [Period(date(2000, 1, 1), date(2000, 1, 14)),
         Period(date(2000, 1, 15), date(2000, 2, 1)),
         Period(date(2000, 2, 2), date(2000, 2, 15))]

def test_separated_period(test_period):
    """separated periods"""
    assert flat_overlap([test_period, Period(date(2000, 2, 16), date(2000, 3, 1))]) == \
        [Period(date(2000, 1, 1), date(2000, 2, 15)),
         Period(date(2000, 2, 16), date(2000, 3, 1))]

def test_duplicate_period(test_period):
    """duplicated periods"""
    assert flat_overlap([test_period, Period(date(2000, 1, 1), date(2000, 2, 15))]) == \
        [Period(date(2000, 1, 1), date(2000, 2, 15))]

def test_same_start(test_period):
    """has same start"""
    assert flat_overlap([test_period, Period(date(2000, 1, 1), date(2000, 3, 15))]) == \
        [Period(date(2000, 1, 1), date(2000, 2, 15)),
         Period(date(2000, 2, 16), date(2000, 3, 15))]

def test_same_end(test_period):
    """has same end"""
    assert flat_overlap([test_period, Period(date(2000, 2, 1), date(2000, 2, 15))]) == \
        [Period(date(2000, 1, 1), date(2000, 1, 31)),
         Period(date(2000, 2, 1), date(2000, 2, 15))]

def test_sort(test_period):
    """sorting"""
    periods = [test_period, 
               Period(date(2000, 1, 1), date(2000, 3, 15)),
               Period(date(1999, 1, 1), date(2000, 3, 15)),
               Period(date(2000, 2, 1), date(2000, 2, 15)),]

    assert sorted(periods) == [
        Period(date(1999, 1, 1), date(2000, 3, 15)),
        test_period, 
        Period(date(2000, 1, 1), date(2000, 3, 15)),
        Period(date(2000, 2, 1), date(2000, 2, 15)),]

    periods.sort()
    assert periods == [
        Period(date(1999, 1, 1), date(2000, 3, 15)),
        test_period, 
        Period(date(2000, 1, 1), date(2000, 3, 15)),
        Period(date(2000, 2, 1), date(2000, 2, 15)),]
    
    
