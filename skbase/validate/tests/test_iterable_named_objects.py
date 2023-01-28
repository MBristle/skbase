# -*- coding: utf-8 -*-
# copyright: skbase developers, BSD-3-Clause License (see LICENSE file)
"""Tests of the functionality for validating iterables of named objects.

tests in this module:


"""

__author__ = ["RNKuhns"]
import pytest

from skbase.base import BaseEstimator, BaseObject
from skbase.validate import check_iterable_named_objects, is_iterable_named_objects


@pytest.fixture
def fixture_object_instance():
    """Pytest fixture of BaseObject instance."""
    return BaseObject()


@pytest.fixture
def fixture_estimator_instance():
    """Pytest fixture of BaseEstimator instance."""
    return BaseEstimator()


def test_is_iterable_named_objects_output(
    fixture_estimator_instance, fixture_object_instance
):
    """Test is_iterable_named_objects returns expected value."""
    # Correctly formatted iterables of (name, BaseObject instance) tuples
    iterable_of_named_objects = [
        ("Step 1", fixture_estimator_instance),
        ("Step 2", fixture_object_instance),
    ]
    assert is_iterable_named_objects(iterable_of_named_objects) is True
    assert is_iterable_named_objects(tuple(iterable_of_named_objects)) is True

    # Test correct format, but duplicate names
    iterable_of_named_objects = [
        ("Step 1", fixture_estimator_instance),
        ("Step 1", fixture_object_instance),
    ]
    assert is_iterable_named_objects(iterable_of_named_objects) is True
    assert is_iterable_named_objects(tuple(iterable_of_named_objects)) is True
    # Tests with correctly formatted dictionary
    dict_named_objects = {
        "Step 1": fixture_estimator_instance,
        "Step 2": fixture_object_instance,
    }
    assert is_iterable_named_objects(dict_named_objects) is True
    assert is_iterable_named_objects(dict_named_objects, allow_dict=False) is False

    # Invalid format due to object names not being strings
    iterable_incorrectly_named_objects = [
        (1, fixture_estimator_instance),
        (2, fixture_object_instance),
    ]
    assert is_iterable_named_objects(iterable_incorrectly_named_objects) is False

    # Invalid format due to named items not being BaseObject instances
    iterable_named_items = [("1", 7), ("2", 42)]
    assert is_iterable_named_objects(iterable_named_items) is False
    dict_named_objects = {"Step 1": 7, "Step 2": 42}
    assert is_iterable_named_objects(dict_named_objects) is False


def test_check_iterable_named_objects_output(
    fixture_estimator_instance, fixture_object_instance
):
    """Test check_iterable_named_objects returns expected value."""
    # Correctly formatted iterables of (name, BaseObject instance) tuples
    iterable_of_named_objects = [
        ("Step 1", fixture_estimator_instance),
        ("Step 2", fixture_object_instance),
    ]
    assert (
        check_iterable_named_objects(iterable_of_named_objects)
        == iterable_of_named_objects
    )
    assert check_iterable_named_objects(tuple(iterable_of_named_objects)) == tuple(
        iterable_of_named_objects
    )

    # Tests with correctly formatted dictionary
    dict_named_objects = {
        "Step 1": fixture_estimator_instance,
        "Step 2": fixture_object_instance,
    }
    assert check_iterable_named_objects(dict_named_objects) == dict_named_objects
    # Raises an error if we don't allow dicts as part of named object API
    with pytest.raises(ValueError):
        check_iterable_named_objects(dict_named_objects, allow_dict=False)

    # Invalid format due to object names not being strings
    iterable_incorrectly_named_objects = [
        (1, fixture_estimator_instance),
        (2, fixture_object_instance),
    ]
    with pytest.raises(ValueError):
        check_iterable_named_objects(iterable_incorrectly_named_objects)

    # Invalid format due to named items not being BaseObject instances
    iterable_named_items = [("1", 7), ("2", 42)]
    with pytest.raises(ValueError):
        check_iterable_named_objects(iterable_named_items)
    dict_named_objects = {"Step 1": 7, "Step 2": 42}
    with pytest.raises(ValueError):
        check_iterable_named_objects(dict_named_objects)
