# -*- coding: utf-8 -*-
# copyright: skbase developers, BSD-3-Clause License (see LICENSE file)
# Elements of these tests re-use code developed in scikit-learn. These elements
# are copyrighted by the scikit-learn developers, BSD-3-Clause License. For
# conditions see https://github.com/scikit-learn/scikit-learn/blob/main/COPYING
"""Tests for BaseObject universal base class.

tests in this module:

    test_get_class_tags  - tests get_class_tags inheritance logic
    test_get_class_tag   - tests get_class_tag logic, incl default value
    test_get_tags        - tests get_tags inheritance logic
    test_get_tag         - tests get_tag logic, incl default value
    test_set_tags        - tests set_tags logic and related get_tags inheritance

    test_reset           - tests reset logic on a simple, non-composite estimator
    test_reset_composite - tests reset logic on a composite estimator
    test_components      - tests logic for returning components of composite estimator
"""

__author__ = ["fkiraly", "RNKuhns"]

__all__ = [
    "test_get_class_tags",
    "test_get_class_tag",
    "test_get_tags",
    "test_get_tag",
    "test_get_tag_raises",
    "test_set_tags",
    "test_set_tags_works_with_missing_tags_dynamic_attribute",
    "test_clone_tags",
    "test_is_composite",
    "test_components",
    "test_components_raises_error_base_class_is_not_class",
    "test_components_raises_error_base_class_is_not_baseobject_subclass",
    "test_reset",
    "test_reset_composite",
    "test_get_init_signature",
    "test_get_init_signature_raises_error_for_invalid_signature",
    "test_get_param_names",
    "test_get_params",
    "test_get_params_invariance",
    "test_get_params_after_set_params",
    "test_set_params",
    "test_set_params_raises_error_non_existent_param",
    "test_set_params_raises_error_non_interface_composite",
    "test_raises_on_get_params_for_param_arg_not_assigned_to_attribute",
    "test_set_params_with_no_param_to_set_returns_object",
    "test_clone",
    "test_clone_2",
    "test_clone_raises_error_for_nonconforming_objects",
    "test_clone_param_is_none",
    "test_clone_empty_array",
    "test_clone_sparse_matrix",
    "test_clone_nan",
    "test_clone_estimator_types",
    "test_clone_class_rather_than_instance_raises_error",
    "test_baseobject_repr",
    "test_baseobject_str",
    "test_baseobject_repr_mimebundle_",
    "test_repr_html_wraps",
    "test_get_test_params",
    "test_get_test_params_raises_error_when_params_required",
    "test_create_test_instance",
    "test_create_test_instances_and_names",
    "test_has_implementation_of",
]

import inspect
from copy import deepcopy

import numpy as np
import pytest
import scipy.sparse as sp
from sklearn import config_context

# TODO: Update with import of skbase clone function once implemented
from sklearn.base import clone

from skbase.base import BaseObject
from skbase.tests.conftest import (
    Buggy,
    CompositionDummy,
    FixtureClassChild,
    FixtureClassParent,
    InvalidInitSignatureTester,
    ModifyParam,
    NoParamInterface,
    RequiredParam,
    ResetTester,
)

# TODO: Determine if we need to add sklearn style test of
# test_set_params_passes_all_parameters


@pytest.fixture
def fixture_object():
    """Pytest fixture of BaseObject class."""
    return BaseObject


@pytest.fixture
def fixture_class_parent():
    """Pytest fixture for FixtureClassParent."""
    return FixtureClassParent


@pytest.fixture
def fixture_class_child():
    """Pytest fixture for FixtureClassChild."""
    return FixtureClassChild


@pytest.fixture
def fixture_class_parent_instance():
    """Pytest fixture for instance of FixtureClassParent."""
    return FixtureClassParent()


@pytest.fixture
def fixture_class_child_instance():
    """Pytest fixture for instance of FixtureClassChild."""
    return FixtureClassChild()


# Fixture class for testing tag system, object overrides class tags
@pytest.fixture
def fixture_tag_class_object():
    """Fixture class for testing tag system, object overrides class tags."""
    fixture_class_child = FixtureClassChild()
    fixture_class_child._tags_dynamic = {"A": 42424241, "B": 3}
    return fixture_class_child


@pytest.fixture
def fixture_composition_dummy():
    """Pytest fixture for CompositionDummy."""
    return CompositionDummy


@pytest.fixture
def fixture_reset_tester():
    """Pytest fixture for ResetTester."""
    return ResetTester


@pytest.fixture
def fixture_class_child_tags(fixture_class_child):
    """Pytest fixture for tags of FixtureClassChild."""
    return fixture_class_child.get_class_tags()


@pytest.fixture
def fixture_object_instance_set_tags(fixture_tag_class_object):
    """Fixture class instance to test tag setting."""
    fixture_tag_set = {"A": 42424243, "E": 3}
    return fixture_tag_class_object.set_tags(**fixture_tag_set)


@pytest.fixture
def fixture_object_tags():
    """Fixture object tags."""
    return {"A": 42424241, "B": 3, "C": 1234, 3: "E"}


@pytest.fixture
def fixture_object_set_tags():
    """Fixture object tags."""
    return {"A": 42424243, "B": 3, "C": 1234, 3: "E", "E": 3}


@pytest.fixture
def fixture_object_dynamic_tags():
    """Fixture object tags."""
    return {"A": 42424243, "B": 3, "E": 3}


@pytest.fixture
def fixture_invalid_init():
    """Pytest fixture class for InvalidInitSignatureTester."""
    return InvalidInitSignatureTester


@pytest.fixture
def fixture_required_param():
    """Pytest fixture class for RequiredParam."""
    return RequiredParam


@pytest.fixture
def fixture_buggy():
    """Pytest fixture class for RequiredParam."""
    return Buggy


@pytest.fixture
def fixture_modify_param():
    """Pytest fixture class for RequiredParam."""
    return ModifyParam


@pytest.fixture
def fixture_class_parent_expected_params():
    """Pytest fixture class for expected params of FixtureClassParent."""
    return {"a": "something", "b": 7, "c": None}


@pytest.fixture
def fixture_class_instance_no_param_interface():
    """Pytest fixture class instance for NoParamInterface."""
    return NoParamInterface()


def test_get_class_tags(fixture_class_child, fixture_class_child_tags):
    """Test get_class_tags class method of BaseObject for correctness.

    Raises
    ------
    AssertError if inheritance logic in get_class_tags is incorrect
    """
    child_tags = fixture_class_child.get_class_tags()

    msg = "Inheritance logic in BaseObject.get_class_tags is incorrect"

    assert child_tags == fixture_class_child_tags, msg


def test_get_class_tag(fixture_class_child, fixture_class_child_tags):
    """Test get_class_tag class method of BaseObject for correctness.

    Raises
    ------
    AssertError if inheritance logic in get_tag is incorrect
    AssertError if default override logic in get_tag is incorrect
    """
    child_tags = {}

    for key in fixture_class_child_tags:
        child_tags[key] = fixture_class_child.get_class_tag(key)

    child_tag_default = fixture_class_child.get_class_tag("foo", "bar")
    child_tag_default_none = fixture_class_child.get_class_tag("bar")

    msg = "Inheritance logic in BaseObject.get_class_tag is incorrect"

    for key in fixture_class_child_tags:
        assert child_tags[key] == fixture_class_child_tags[key], msg

    msg = "Default override logic in BaseObject.get_class_tag is incorrect"

    assert child_tag_default == "bar", msg
    assert child_tag_default_none is None, msg


def test_get_tags(fixture_tag_class_object, fixture_object_tags):
    """Test get_tags method of BaseObject for correctness.

    Raises
    ------
    AssertError if inheritance logic in get_tags is incorrect
    """
    object_tags = fixture_tag_class_object.get_tags()

    msg = "Inheritance logic in BaseObject.get_tags is incorrect"

    assert object_tags == fixture_object_tags, msg


def test_get_tag(fixture_tag_class_object, fixture_object_tags):
    """Test get_tag method of BaseObject for correctness.

    Raises
    ------
    AssertError if inheritance logic in get_tag is incorrect
    AssertError if default override logic in get_tag is incorrect
    """
    object_tags = {}
    object_tags_keys = fixture_object_tags.keys()

    for key in object_tags_keys:
        object_tags[key] = fixture_tag_class_object.get_tag(key, raise_error=False)

    object_tag_default = fixture_tag_class_object.get_tag(
        "foo", "bar", raise_error=False
    )
    object_tag_default_none = fixture_tag_class_object.get_tag("bar", raise_error=False)

    msg = "Inheritance logic in BaseObject.get_tag is incorrect"

    for key in object_tags_keys:
        assert object_tags[key] == fixture_object_tags[key], msg

    msg = "Default override logic in BaseObject.get_tag is incorrect"

    assert object_tag_default == "bar", msg
    assert object_tag_default_none is None, msg


def test_get_tag_raises(fixture_tag_class_object):
    """Test that get_tag method raises error for unknown tag.

    Raises
    ------
    AssertError if get_tag does not raise error for unknown tag.
    """
    with pytest.raises(ValueError, match=r"Tag with name"):
        fixture_tag_class_object.get_tag("bar")


def test_set_tags(
    fixture_object_instance_set_tags,
    fixture_object_set_tags,
    fixture_object_dynamic_tags,
):
    """Test set_tags method of BaseObject for correctness.

    Raises
    ------
    AssertionError if override logic in set_tags is incorrect
    """
    msg = "Setter/override logic in BaseObject.set_tags is incorrect"

    assert (
        fixture_object_instance_set_tags._tags_dynamic == fixture_object_dynamic_tags
    ), msg
    assert fixture_object_instance_set_tags.get_tags() == fixture_object_set_tags, msg


def test_set_tags_works_with_missing_tags_dynamic_attribute(fixture_tag_class_object):
    """Test set_tags will still work if _tags_dynamic is missing."""
    base_obj = deepcopy(fixture_tag_class_object)
    delattr(base_obj, "_tags_dynamic")
    assert not hasattr(base_obj, "_tags_dynamic")
    base_obj.set_tags(some_tag="something")
    tags = base_obj.get_tags()
    assert hasattr(base_obj, "_tags_dynamic")
    assert "some_tag" in tags and tags["some_tag"] == "something"


def test_clone_tags():
    """Test clone_tags works as expected."""

    class TestClass(BaseObject):
        _tags = {"some_tag": True, "another_tag": 37}

    class AnotherTestClass(BaseObject):
        pass

    # Simple example of cloning all tags with no tags overlapping
    base_obj = AnotherTestClass()
    test_obj = TestClass()
    assert base_obj.get_tags() == {}
    base_obj.clone_tags(test_obj)
    assert base_obj.get_class_tags() == {}
    assert base_obj.get_tags() == test_obj.get_tags()

    # Simple examples cloning named tags with no tags overlapping
    base_obj = AnotherTestClass()
    test_obj = TestClass()
    assert base_obj.get_tags() == {}
    base_obj.clone_tags(test_obj, tag_names="some_tag")
    assert base_obj.get_class_tags() == {}
    assert base_obj.get_tags() == {"some_tag": True}
    base_obj.clone_tags(test_obj, tag_names=["another_tag"])
    assert base_obj.get_class_tags() == {}
    assert base_obj.get_tags() == test_obj.get_tags()

    # Overlapping tag example where there is tags in each object that aren't
    # in the other object
    another_base_obj = AnotherTestClass()
    another_base_obj.set_tags(some_tag=False, a_new_tag="words")
    another_base_obj_tags = another_base_obj.get_tags()
    test_obj = TestClass()
    assert test_obj.get_tags() == TestClass.get_class_tags()
    test_obj.clone_tags(another_base_obj)
    test_obj_tags = test_obj.get_tags()
    assert test_obj.get_class_tags() == TestClass.get_class_tags()
    # Verify all tags in another_base_obj were cloned into test_obj
    for tag in another_base_obj_tags:
        assert test_obj_tags.get(tag) == another_base_obj_tags[tag]
    # Verify tag that was in test_obj but not another_base_obj still has same value
    # and there aren't any other tags
    assert (
        "another_tag" in test_obj_tags
        and test_obj_tags["another_tag"] == 37
        and len(test_obj_tags) == 3
    )

    # Overlapping tag example using named tags in clone
    another_base_obj = AnotherTestClass()
    another_base_obj.set_tags(some_tag=False, a_new_tag="words")
    another_base_obj_tags = another_base_obj.get_tags()
    test_obj = TestClass()
    assert test_obj.get_tags() == TestClass.get_class_tags()
    test_obj.clone_tags(another_base_obj, tag_names=["a_new_tag"])
    test_obj_tags = test_obj.get_tags()
    assert test_obj.get_class_tags() == TestClass.get_class_tags()
    assert test_obj_tags.get("a_new_tag") == "words"

    # Verify all tags in another_base_obj were cloned into test_obj
    test_obj = TestClass()
    test_obj.clone_tags(another_base_obj)
    test_obj_tags = test_obj.get_tags()
    for tag in another_base_obj_tags:
        assert test_obj_tags.get(tag) == another_base_obj_tags[tag]


def test_is_composite(fixture_composition_dummy):
    """Test is_composite tag for correctness.

    Raises
    ------
    AssertionError if logic behind is_composite is incorrect
    """
    non_composite = fixture_composition_dummy(foo=42)
    composite = fixture_composition_dummy(foo=non_composite)

    assert not non_composite.is_composite()
    assert composite.is_composite()


def test_components(fixture_object, fixture_class_parent, fixture_composition_dummy):
    """Test component retrieval.

    Raises
    ------
    AssertionError if logic behind _components is incorrect, logic tested:
        calling _components on a non-composite returns an empty dict
        calling _components on a composite returns name/BaseObject pair in dict,
        and BaseObject returned is identical with attribute of the same name
    """
    non_composite = fixture_composition_dummy(foo=42)
    composite = fixture_composition_dummy(foo=non_composite)

    non_comp_comps = non_composite._components()
    comp_comps = composite._components()
    comp_comps_baseobject_filter = composite._components(fixture_object)
    comp_comps_filter = composite._components(fixture_class_parent)

    assert isinstance(non_comp_comps, dict)
    assert set(non_comp_comps.keys()) == set()

    assert isinstance(comp_comps, dict)
    assert set(comp_comps.keys()) == {"foo_"}
    assert comp_comps["foo_"] == composite.foo_
    assert comp_comps["foo_"] != composite.foo

    assert comp_comps == comp_comps_baseobject_filter
    assert comp_comps_filter == {}


def test_components_raises_error_base_class_is_not_class(
    fixture_object, fixture_composition_dummy
):
    """Test _component method raises error if base_class param is not class."""
    non_composite = fixture_composition_dummy(foo=42)
    composite = fixture_composition_dummy(foo=non_composite)
    with pytest.raises(
        TypeError, match="base_class must be a class, but found <class 'int'>"
    ):
        composite._components(7)

    msg = "base_class must be a class, but found <class 'skbase.base._base.BaseObject'>"
    with pytest.raises(
        TypeError,
        match=msg,
    ):
        composite._components(fixture_object())


def test_components_raises_error_base_class_is_not_baseobject_subclass(
    fixture_composition_dummy,
):
    """Test _component method raises error if base_class is not BaseObject subclass."""

    class SomeClass:
        pass

    composite = fixture_composition_dummy(foo=SomeClass())
    with pytest.raises(TypeError, match="base_class must be a subclass of BaseObject"):
        composite._components(SomeClass)


# Test parameter interface (get_params, set_params, reset and related methods)
# Some tests of get_params and set_params are adapted from sklearn tests
def test_reset(fixture_reset_tester):
    """Test reset method for correct behaviour, on a simple estimator.

    Raises
    ------
    AssertionError if logic behind reset is incorrect, logic tested:
        reset should remove any object attributes that are not hyper-parameters,
        with the exception of attributes containing double-underscore "__"
        reset should not remove class attributes or methods
        reset should set hyper-parameters as in pre-reset state
    """
    x = fixture_reset_tester(168)
    x.foo()

    x.reset()

    assert hasattr(x, "a") and x.a == 168
    assert hasattr(x, "b") and x.b == 42
    assert hasattr(x, "c") and x.c == 84
    assert hasattr(x, "clsvar") and x.clsvar == 210
    assert not hasattr(x, "d")
    assert not hasattr(x, "_d")
    assert not hasattr(x, "d_")
    assert hasattr(x, "f__o__o") and x.f__o__o == 252
    assert hasattr(x, "foo")


def test_reset_composite(fixture_reset_tester):
    """Test reset method for correct behaviour, on a composite estimator."""
    y = fixture_reset_tester(42)
    x = fixture_reset_tester(a=y)

    x.foo(y)
    x.d.foo()

    x.reset()

    assert hasattr(x, "a")
    assert not hasattr(x, "d")
    assert not hasattr(x.a, "d")


def test_get_init_signature(fixture_class_parent):
    """Test error is raised when invalid init signature is used."""
    init_sig = fixture_class_parent._get_init_signature()
    init_sig_is_list = isinstance(init_sig, list)
    init_sig_elements_are_params = all(
        isinstance(p, inspect.Parameter) for p in init_sig
    )
    assert (
        init_sig_is_list and init_sig_elements_are_params
    ), "`_get_init_signature` is not returning expected result."


def test_get_init_signature_raises_error_for_invalid_signature(fixture_invalid_init):
    """Test error is raised when invalid init signature is used."""
    with pytest.raises(RuntimeError):
        fixture_invalid_init._get_init_signature()


def test_get_param_names(
    fixture_object, fixture_class_parent, fixture_class_parent_expected_params
):
    """Test that get_param_names returns list of string parameter names."""
    param_names = fixture_class_parent.get_param_names()
    assert param_names == sorted([*fixture_class_parent_expected_params])

    param_names = fixture_object.get_param_names()
    assert param_names == []


def test_get_params(
    fixture_class_parent,
    fixture_class_parent_expected_params,
    fixture_class_instance_no_param_interface,
    fixture_composition_dummy,
):
    """Test get_params returns expected parameters."""
    # Simple test of returned params
    base_obj = fixture_class_parent()
    params = base_obj.get_params()
    assert params == fixture_class_parent_expected_params

    # Test get_params with composite object
    composite = fixture_composition_dummy(foo=base_obj, bar=84)
    params = composite.get_params()
    assert "foo__a" in params and "foo__b" in params and "foo__c" in params
    assert "bar" in params and params["bar"] == 84
    assert "foo" in params and isinstance(params["foo"], fixture_class_parent)
    assert "foo__a" not in composite.get_params(deep=False)

    # Since NoParamInterface does not have get_params we should just return
    # "foo" and "bar" in params and no other parameters
    composite = fixture_composition_dummy(foo=fixture_class_instance_no_param_interface)
    params = composite.get_params()
    assert "foo" in params and "bar" in params and len(params) == 2


def test_get_params_invariance(fixture_class_parent, fixture_composition_dummy):
    """Test that get_params(deep=False) is subset of get_params(deep=True)."""
    composite = fixture_composition_dummy(foo=fixture_class_parent(), bar=84)
    shallow_params = composite.get_params(deep=False)
    deep_params = composite.get_params(deep=True)
    assert all(item in deep_params.items() for item in shallow_params.items())


def test_get_params_after_set_params(fixture_class_parent):
    """Test that get_params returns the same thing before and after set_params.

    Based on scikit-learn check in check_estimator.
    """
    base_obj = fixture_class_parent()

    orig_params = base_obj.get_params(deep=False)
    msg = "get_params result does not match what was passed to set_params"

    base_obj.set_params(**orig_params)
    curr_params = base_obj.get_params(deep=False)
    assert set(orig_params.keys()) == set(curr_params.keys()), msg
    for k, v in curr_params.items():
        assert orig_params[k] is v, msg

    # some fuzz values
    test_values = [-np.inf, np.inf, None]

    test_params = deepcopy(orig_params)
    for param_name in orig_params.keys():
        default_value = orig_params[param_name]
        for value in test_values:
            test_params[param_name] = value
            try:
                base_obj.set_params(**test_params)
            except (TypeError, ValueError):
                params_before_exception = curr_params
                curr_params = base_obj.get_params(deep=False)
                assert set(params_before_exception.keys()) == set(curr_params.keys())
                for k, v in curr_params.items():
                    assert params_before_exception[k] is v
            else:
                curr_params = base_obj.get_params(deep=False)
                assert set(test_params.keys()) == set(curr_params.keys()), msg
                for k, v in curr_params.items():
                    assert test_params[k] is v, msg
        test_params[param_name] = default_value


def test_set_params(
    fixture_class_parent,
    fixture_class_parent_expected_params,
    fixture_composition_dummy,
):
    """Test set_params works as expected."""
    # Simple case of setting a parameter
    base_obj = fixture_class_parent()
    base_obj.set_params(b="updated param value")
    expected_params = deepcopy(fixture_class_parent_expected_params)
    expected_params["b"] = "updated param value"
    assert base_obj.get_params() == expected_params

    # Setting parameter of a composite class
    composite = fixture_composition_dummy(foo=fixture_class_parent(), bar=84)
    composite.set_params(bar=95, foo__b="updated param value")
    params = composite.get_params()
    assert params["bar"] == 95
    assert (
        params["foo__b"] == "updated param value"
        and composite.foo.b == "updated param value"
    )


def test_set_params_raises_error_non_existent_param(
    fixture_class_parent_instance, fixture_composition_dummy
):
    """Test set_params raises an error when passed a non-existent parameter name."""
    # non-existing parameter in svc
    with pytest.raises(ValueError):
        fixture_class_parent_instance.set_params(
            non_existant_param="updated param value"
        )

    # non-existing parameter of composite
    composite = fixture_composition_dummy(foo=fixture_class_parent_instance, bar=84)
    with pytest.raises(ValueError):
        composite.set_params(foo__non_existant_param=True)


def test_set_params_raises_error_non_interface_composite(
    fixture_class_instance_no_param_interface, fixture_composition_dummy
):
    """Test set_params raises error when setting param of non-conforming composite."""
    # When a composite is made up of a class that doesn't have the BaseObject
    # parameter interface, we should get a AttributeError when trying to
    # set the composite's params
    composite = fixture_composition_dummy(foo=fixture_class_instance_no_param_interface)
    with pytest.raises(AttributeError):
        composite.set_params(foo__a=88)


def test_raises_on_get_params_for_param_arg_not_assigned_to_attribute():
    """Test get_params raises error if param not assigned to same named attribute."""

    class BadObject(BaseObject):
        # Here we don't assign param to self.param as expected in interface
        def __init__(self, param=5):
            super().__init__()

    est = BadObject()
    msg = "'BadObject' object has no attribute 'param'"

    with pytest.raises(AttributeError, match=msg):
        est.get_params()


def test_set_params_with_no_param_to_set_returns_object(fixture_class_parent):
    """Test set_params correctly returns self when no parameters are set."""
    base_obj = fixture_class_parent()
    orig_params = deepcopy(base_obj.get_params())
    base_obj_set_params = base_obj.set_params()
    assert (
        isinstance(base_obj_set_params, fixture_class_parent)
        and base_obj_set_params.get_params() == orig_params
    )


# This section tests the clone functionality
# These have been adapted from sklearn's tests of clone to use the clone
# method that is included as part of the BaseObject interface
def test_clone(fixture_class_parent_instance):
    """Test that clone is making a deep copy as expected."""
    # Creates a BaseObject and makes a copy of its original state
    # (which, in this case, is the current state of the BaseObject),
    # and check that the obtained copy is a correct deep copy.
    new_base_obj = fixture_class_parent_instance.clone()
    assert fixture_class_parent_instance is not new_base_obj
    assert fixture_class_parent_instance.get_params() == new_base_obj.get_params()


def test_clone_2(fixture_class_parent_instance):
    """Test that clone does not copy attributes not set in constructor."""
    # We first create an estimator, give it an own attribute, and
    # make a copy of its original state. Then we check that the copy doesn't
    # have the specific attribute we manually added to the initial estimator.

    # base_obj = fixture_class_parent(a=7.0, b="some_str")
    fixture_class_parent_instance.own_attribute = "test"
    new_base_obj = fixture_class_parent_instance.clone()
    assert not hasattr(new_base_obj, "own_attribute")


def test_clone_raises_error_for_nonconforming_objects(
    fixture_invalid_init, fixture_buggy, fixture_modify_param
):
    """Test that clone raises an error on nonconforming BaseObjects."""
    buggy = fixture_buggy()
    buggy.a = 2
    with pytest.raises(RuntimeError):
        buggy.clone()

    varg_obj = fixture_invalid_init(a=7)
    with pytest.raises(RuntimeError):
        varg_obj.clone()

    obj_that_modifies = fixture_modify_param(a=[0])
    with pytest.raises(RuntimeError):
        obj_that_modifies.clone()


def test_clone_param_is_none(fixture_class_parent):
    """Test clone with keyword parameter set to None."""
    base_obj = fixture_class_parent(c=None)
    new_base_obj = clone(base_obj)
    new_base_obj2 = base_obj.clone()
    assert base_obj.c is new_base_obj.c
    assert base_obj.c is new_base_obj2.c


def test_clone_empty_array(fixture_class_parent):
    """Test clone with keyword parameter is scipy sparse matrix.

    This test is based on scikit-learn regression test to make sure clone
    works with default parameter set to scipy sparse matrix.
    """
    # Regression test for cloning estimators with empty arrays
    base_obj = fixture_class_parent(c=np.array([]))
    new_base_obj = clone(base_obj)
    new_base_obj2 = base_obj.clone()
    np.testing.assert_array_equal(base_obj.c, new_base_obj.c)
    np.testing.assert_array_equal(base_obj.c, new_base_obj2.c)


def test_clone_sparse_matrix(fixture_class_parent):
    """Test clone with keyword parameter is scipy sparse matrix.

    This test is based on scikit-learn regression test to make sure clone
    works with default parameter set to scipy sparse matrix.
    """
    base_obj = fixture_class_parent(c=sp.csr_matrix(np.array([[0]])))
    new_base_obj = clone(base_obj)
    new_base_obj2 = base_obj.clone()
    np.testing.assert_array_equal(base_obj.c, new_base_obj.c)
    np.testing.assert_array_equal(base_obj.c, new_base_obj2.c)


def test_clone_nan(fixture_class_parent):
    """Test clone with keyword parameter is np.nan.

    This test is based on scikit-learn regression test to make sure clone
    works with default parameter set to np.nan.
    """
    # Regression test for cloning estimators with default parameter as np.nan
    base_obj = fixture_class_parent(c=np.nan)
    new_base_obj = clone(base_obj)
    new_base_obj2 = base_obj.clone()

    assert base_obj.c is new_base_obj.c
    assert base_obj.c is new_base_obj2.c


def test_clone_estimator_types(fixture_class_parent):
    """Test clone works for parameters that are types rather than instances."""
    base_obj = fixture_class_parent(c=fixture_class_parent)
    new_base_obj = base_obj.clone()

    assert base_obj.c == new_base_obj.c


def test_clone_class_rather_than_instance_raises_error(fixture_class_parent):
    """Test clone raises expected error when cloning a class instead of an instance."""
    msg = "You should provide an instance of scikit-learn estimator"
    with pytest.raises(TypeError, match=msg):
        clone(fixture_class_parent)


# Tests of BaseObject pretty printing representation inspired by sklearn
def test_baseobject_repr(fixture_class_parent, fixture_composition_dummy):
    """Test BaseObject repr works as expected."""
    # Simple test where all parameters are left at defaults
    # Should not see parameters and values in printed representation
    base_obj = fixture_class_parent()
    assert repr(base_obj) == "FixtureClassParent()"

    # Check that we can alter the detail about params that is printed
    # using config_context with ``print_changed_only=False``
    with config_context(print_changed_only=False):
        assert repr(base_obj) == "FixtureClassParent(a='something', b=7, c=None)"

    simple_composite = fixture_composition_dummy(foo=fixture_class_parent())
    assert repr(simple_composite) == "CompositionDummy(foo=FixtureClassParent())"

    long_base_obj_repr = fixture_class_parent(a=["long_params"] * 1000)
    assert len(repr(long_base_obj_repr)) == 675


def test_baseobject_str(fixture_class_parent_instance):
    """Test BaseObject string representation works."""
    str(fixture_class_parent_instance)


def test_baseobject_repr_mimebundle_(fixture_class_parent_instance):
    """Test display configuration controls output."""
    # Checks the display configuration flag controls the json output
    with config_context(display="diagram"):
        output = fixture_class_parent_instance._repr_mimebundle_()
        assert "text/plain" in output
        assert "text/html" in output

    with config_context(display="text"):
        output = fixture_class_parent_instance._repr_mimebundle_()
        assert "text/plain" in output
        assert "text/html" not in output


def test_repr_html_wraps(fixture_class_parent_instance):
    """Test display configuration flag controls the html output."""
    with config_context(display="diagram"):
        output = fixture_class_parent_instance._repr_html_()
        assert "<style>" in output

    with config_context(display="text"):
        msg = "_repr_html_ is only defined when"
        with pytest.raises(AttributeError, match=msg):
            fixture_class_parent_instance._repr_html_()


# Test BaseObject's ability to generate test instances
def test_get_test_params(fixture_class_parent_instance):
    """Test get_test_params returns empty dictionary."""
    base_obj = fixture_class_parent_instance
    test_params = base_obj.get_test_params()
    assert isinstance(test_params, dict) and len(test_params) == 0


def test_get_test_params_raises_error_when_params_required(fixture_required_param):
    """Test get_test_params raises an error when parameters are required."""
    with pytest.raises(ValueError):
        fixture_required_param().get_test_params()


def test_create_test_instance(fixture_class_parent, fixture_class_parent_instance):
    """Test first that create_test_instance logic works."""
    base_obj = fixture_class_parent.create_test_instance()

    # Check that init does not construct object of other class than itself
    assert isinstance(base_obj, fixture_class_parent_instance.__class__), (
        "Object returned by create_test_instance must be an instance of the class, "
        f"but found {type(base_obj)}."
    )

    msg = (
        f"{fixture_class_parent.__name__}.__init__ should call "
        f"super({fixture_class_parent.__name__}, self).__init__, "
        "but that does not seem to be the case. Please ensure to call the "
        f"parent class's constructor in {fixture_class_parent.__name__}.__init__"
    )
    assert hasattr(base_obj, "_tags_dynamic"), msg


def test_create_test_instances_and_names(fixture_class_parent_instance):
    """Test that create_test_instances_and_names works."""
    base_objs, names = fixture_class_parent_instance.create_test_instances_and_names()

    assert isinstance(base_objs, list), (
        "First return of create_test_instances_and_names must be a list, "
        f"but found {type(base_objs)}."
    )
    assert isinstance(names, list), (
        "Second return of create_test_instances_and_names must be a list, "
        f"but found {type(names)}."
    )

    assert all(
        [isinstance(est, fixture_class_parent_instance.__class__) for est in base_objs]
    ), (
        "List elements of first return returned by create_test_instances_and_names "
        "all must be an instance of the class"
    )

    assert all([isinstance(name, str) for name in names]), (
        "List elements of second return returned by create_test_instances_and_names"
        " all must be strings."
    )

    assert len(base_objs) == len(names), (
        "The two lists returned by create_test_instances_and_names must have "
        "equal length."
    )


# Tests _has_implementation_of interface
def test_has_implementation_of(
    fixture_class_parent_instance, fixture_class_child_instance
):
    """Test _has_implementation_of detects methods in class with overrides in mro."""
    # When the class overrides a parent classes method should return True
    assert fixture_class_child_instance._has_implementation_of("some_method")
    # When class implements method first time it shoudl return False
    assert not fixture_class_child_instance._has_implementation_of("some_other_method")

    # If the method is defined the first time in the parent class it should not
    # return _has_implementation_of == True
    assert not fixture_class_parent_instance._has_implementation_of("some_method")
