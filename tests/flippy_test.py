import warnings
from dataclasses import dataclass

import pytest

from flippy import Flippy
from flippy.backends import MemoryBackend


@dataclass
class User:
    name: str
    id: int

@dataclass
class Group:
    name: str
    flipper_id: int

@pytest.fixture
def flippy() -> Flippy:
    return Flippy(MemoryBackend())

@pytest.fixture
def get_user():
    users = {}

    def _make_user(name):
        if name not in users:
            try:
                users[name] = max(users.values()) + 1
            except ValueError:
                users[name] = 1
        return User(name, users[name])
    
    return _make_user

@pytest.fixture
def get_group():
    groups = {}

    def _make_group(name):
        if name not in groups:
            try:
                groups[name] = max(groups.values()) + 1
            except ValueError:
                groups[name] = 1
        return Group(name, groups[name])
    
    return _make_group


def test_add_feature(flippy: Flippy):
    assert flippy.create('foo_feature') == True


def test_feature_existence(flippy: Flippy):
    flippy.create('foo_feature')
    assert flippy.feature_exists('foo_feature') == True
    assert flippy.feature_exists('bar_feature') == False


def test_feature_defaults_off(flippy: Flippy):
    flippy.create('foo_feature')
    assert flippy.is_enabled('foo_feature') == False


def test_can_enable_feature(flippy: Flippy):
    flippy.create('foo_feature')
    flippy.enable('foo_feature')
    assert flippy.is_enabled('foo_feature') == True


def test_can_enable_then_disable_feature(flippy: Flippy):
    flippy.create('foo_feature')
    flippy.enable('foo_feature')
    assert flippy.is_enabled('foo_feature') == True
    flippy.disable('foo_feature')
    assert flippy.is_enabled('foo_feature') == False


def test_can_enable_for_actor(flippy: Flippy, get_user):
    flippy.create('actor_feature')
    user1 = get_user('user1')
    user2 = get_user('user2')
    flippy.enable_actor('actor_feature', user1)
    assert flippy.is_enabled('actor_feature', user1) == True
    assert flippy.is_enabled('actor_feature', user2) == False


def test_can_enable_for_group(flippy: Flippy, get_group):
    flippy.create('group_feature')
    group1 = get_group('group1')
    group2 = get_group('group2')
    flippy.enable_actor('group_feature', group1)
    assert flippy.is_enabled('group_feature', group1) == True
    assert flippy.is_enabled('group_feature', group2) == False


def test_boolean_overrides_actor(flippy: Flippy, get_user):
    flippy.create('some_feature')
    flippy.enable('some_feature')
    user1 = get_user('user1')
    user2 = get_user('user2')
    flippy.enable_actor('some_feature', user1)
    assert flippy.is_enabled('some_feature', user1) == True
    assert flippy.is_enabled('some_feature', user2) == True


def test_boolean_overrides_group(flippy: Flippy, get_group):
    flippy.create('some_feature')
    flippy.enable('some_feature')
    group1 = get_group('group1')
    group2 = get_group('group2')
    flippy.enable_actor('some_feature', group1)
    assert flippy.is_enabled('some_feature', group1) == True
    assert flippy.is_enabled('some_feature', group2) == True


def test_can_enable_for_percentage_of_actors(flippy: Flippy, get_user):
    flippy.create('percent_feature')
    flippy.enable_percentage_of_actors('percent_feature', 50)

    # try up to 10 times to find a user which will get the feature
    # and a user which will not get the feature
    user_gets_feature = None
    user_denied_feature = None
    for i in range(10):
        user = get_user(f'user{i}')
        if user_gets_feature is None and flippy.is_enabled('percent_feature', user):
            user_gets_feature = user
        if user_denied_feature is None and not flippy.is_enabled('percent_feature', user):
            user_denied_feature = user
        if user_gets_feature is not None and user_denied_feature is not None:
            break

    if user_gets_feature is None:
        warnings.warn('could not generate a user who gets the feature; test inconclusive')
        return
    if user_denied_feature is None:
        warnings.warn('could not generate a user denied the feature; test inconclusive')
        return

    assert flippy.is_enabled('percent_feature', user_gets_feature) == True
    assert flippy.is_enabled('percent_feature', user_denied_feature) == False

    # now global-enable it
    flippy.enable('percent_feature')
    assert flippy.is_enabled('percent_feature', user_gets_feature) == True
    assert flippy.is_enabled('percent_feature', user_denied_feature) == True

    # now clear the feature
    flippy.clear('percent_feature')
    assert flippy.is_enabled('percent_feature', user_gets_feature) == False
    assert flippy.is_enabled('percent_feature', user_denied_feature) == False


def test_percentage_rollout_is_stable(flippy: Flippy, get_user):
    # We'll generate many users and record how many of them get the feature
    # at 50% rollout. Then we'll play with the rollout number and ensure that
    # a user who is denied at 50% still gets denied as we go down, and likewise
    # a user who is allowed at 50% still gets the feature as we go up.
    #
    # This isn't really conclusive, but with 100 actors and testing several
    # points on the spectrum, it's suggestive of correctness.

    flippy.create('percent_feature')
    flippy.enable_percentage_of_actors('percent_feature', 50)

    users = [get_user(f'user{i}') for i in range(100)]
    states = []
    for user in users:
        states.append(flippy.is_enabled('percent_feature', user))

    # test the descent cases
    for percent in [40, 30, 20, 10]:
        flippy.enable_percentage_of_actors('percent_feature', percent)
        for idx, user in enumerate(users):
            if states[idx] == False:
                assert flippy.is_enabled('percent_feature', user) == False

    # test the ascent cases
    for percent in [60, 70, 80, 90]:
        flippy.enable_percentage_of_actors('percent_feature', percent)
        for idx, user in enumerate(users):
            if states[idx] == True:
                assert flippy.is_enabled('percent_feature', user) == True


def test_can_get_all_features(flippy: Flippy):
    flippy.create('first_feature')
    flippy.create('second_feature')
    flippy.create('third_feature')
    features = flippy.get_all_feature_names()
    assert len(features) == 3
    assert 'first_feature' in features
    assert 'second_feature' in features
    assert 'third_feature' in features
