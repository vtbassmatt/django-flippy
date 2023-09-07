import pytest

from flippy.core import Feature


def test_feature_key_equality():
    f1 = Feature('my_feature')
    f2 = Feature('my_feature')
    assert f1 == f2


def test_feature_key_inequality():
    f1 = Feature('my_feature')
    f2 = Feature('my_other_feature')
    assert f1 != f2


def test_feature_boolean_equality():
    f1 = Feature('my_feature')
    f1.boolean_gate.value = True
    f2 = Feature('my_feature')
    f2.boolean_gate.value = True
    assert f1 == f2


def test_feature_boolean_inequality():
    f1 = Feature('my_feature')
    f1.boolean_gate.value = True
    f2 = Feature('my_feature')
    f2.boolean_gate.value = False
    assert f1 != f2


def test_feature_boolean_none_inequality():
    f1 = Feature('my_feature')
    f1.boolean_gate.value = True
    f2 = Feature('my_feature')
    f2.boolean_gate.value = False
    f3 = Feature('my_feature')
    assert f1 != f3
    assert f2 != f3


def test_feature_actors_simple_equality():
    f1 = Feature('my_feature')
    f1.actors_gate.value = ['user1']
    f2 = Feature('my_feature')
    f2.actors_gate.value = ['user1']
    assert f1 == f2


def test_feature_actors_simple_inequality():
    f1 = Feature('my_feature')
    f1.actors_gate.value = ['user1']
    f2 = Feature('my_feature')
    f2.actors_gate.value = ['user2']
    assert f1 != f2


def test_feature_actors_reorder_equality():
    f1 = Feature('my_feature')
    f1.actors_gate.value = ['user1', 'user2']
    f2 = Feature('my_feature')
    f2.actors_gate.value = ['user2', 'user1']
    assert f1 == f2


def test_feature_actors_list_or_none_inequality():
    f1 = Feature('my_feature')
    f1.actors_gate.value = ['user1']
    f2 = Feature('my_feature')
    f2.actors_gate.value = None
    assert f1 != f2


def test_feature_groups_simple_equality():
    f1 = Feature('my_feature')
    f1.groups_gate.value = ['group1']
    f2 = Feature('my_feature')
    f2.groups_gate.value = ['group1']
    assert f1 == f2


def test_feature_groups_simple_inequality():
    f1 = Feature('my_feature')
    f1.groups_gate.value = ['group1']
    f2 = Feature('my_feature')
    f2.groups_gate.value = ['group2']
    assert f1 != f2


def test_feature_groups_reorder_equality():
    f1 = Feature('my_feature')
    f1.groups_gate.value = ['group1', 'group2']
    f2 = Feature('my_feature')
    f2.groups_gate.value = ['group2', 'group1']
    assert f1 == f2


def test_feature_groups_list_or_none_inequality():
    f1 = Feature('my_feature')
    f1.groups_gate.value = ['group1']
    f2 = Feature('my_feature')
    f2.groups_gate.value = None
    assert f1 != f2


def test_feature_percent_actors_equality():
    f1 = Feature('my_feature')
    f1.percentage_of_actors_gate.value = 30
    f2 = Feature('my_feature')
    f2.percentage_of_actors_gate.value = 30
    assert f1 == f2


def test_feature_percent_actors_inequality():
    f1 = Feature('my_feature')
    f1.percentage_of_actors_gate.value = 30
    f2 = Feature('my_feature')
    f2.percentage_of_actors_gate.value = 40
    assert f1 != f2


def test_feature_percent_actors_none_inequality():
    f1 = Feature('my_feature')
    f1.percentage_of_actors_gate.value = 30
    f2 = Feature('my_feature')
    f2.percentage_of_actors_gate.value = 40
    f3 = Feature('my_feature')
    assert f1 != f3
    assert f2 != f3


def test_feature_percent_actors_zero_inequality():
    f1 = Feature('my_feature')
    f1.percentage_of_actors_gate.value = 0
    f2 = Feature('my_feature')
    assert f1 != f2


def test_feature_percent_time_equality():
    f1 = Feature('my_feature')
    f1.percentage_of_time_gate.value = 30
    f2 = Feature('my_feature')
    f2.percentage_of_time_gate.value = 30
    assert f1 == f2


def test_feature_percent_time_inequality():
    f1 = Feature('my_feature')
    f1.percentage_of_time_gate.value = 30
    f2 = Feature('my_feature')
    f2.percentage_of_time_gate.value = 40
    assert f1 != f2


def test_feature_percent_time_none_inequality():
    f1 = Feature('my_feature')
    f1.percentage_of_time_gate.value = 30
    f2 = Feature('my_feature')
    f2.percentage_of_time_gate.value = 40
    f3 = Feature('my_feature')
    assert f1 != f3
    assert f2 != f3


def test_feature_percent_time_zero_inequality():
    f1 = Feature('my_feature')
    f1.percentage_of_time_gate.value = 0
    f2 = Feature('my_feature')
    assert f1 != f2
