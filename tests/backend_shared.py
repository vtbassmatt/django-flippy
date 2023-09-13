"""
Tests which should run for every backend.
"""
from flippy.backends import BaseBackend
from flippy.core import Gate

# NOTE! Only create features with the prefix listed here. That way our teardown
# for flipper_cloud_test will (attempt to) clean up after itself. Like this:
# my_name = f"{TEST_FEATURE}_foo"
#
# Also, be sure to use a new feature name in each testcase to keep them isolated.
TEST_FEATURE = 'django_flippy_testcase'


def test_add_feature(backend: BaseBackend):
    assert backend.add(f'{TEST_FEATURE}_one') == True


def test_feature_defaults_off(backend: BaseBackend):
    feature_name = f'{TEST_FEATURE}_two'
    backend.add(feature_name)
    f = backend.get(feature_name)
    assert f.state == 'off'


def test_can_enable_feature(backend: BaseBackend):
    feature_name = f'{TEST_FEATURE}_three'
    backend.add(feature_name)
    backend.enable(feature_name, Gate.Boolean)
    f = backend.get(feature_name)
    assert f.state == 'on'


def test_can_enable_then_disable_feature(backend: BaseBackend):
    feature_name = f'{TEST_FEATURE}_four'
    backend.add(feature_name)
    backend.enable(feature_name, Gate.Boolean)
    f = backend.get(feature_name)
    assert f.state == 'on'
    backend.disable(feature_name, Gate.Boolean)
    f = backend.get(feature_name)
    assert f.state == 'off'


def test_can_enumerate_features(backend: BaseBackend):
    backend.add(f'{TEST_FEATURE}_first')
    backend.add(f'{TEST_FEATURE}_second')
    backend.add(f'{TEST_FEATURE}_third')
    features = backend.features()
    assert f'{TEST_FEATURE}_first' in features
    assert f'{TEST_FEATURE}_second' in features
    assert f'{TEST_FEATURE}_third' in features


def test_can_get_some_features(backend: BaseBackend):
    backend.add(f'{TEST_FEATURE}_fourth')
    backend.add(f'{TEST_FEATURE}_fifth')
    features = backend.get_multi([f'{TEST_FEATURE}_fourth', f'{TEST_FEATURE}_fifth'])
    assert len(features) == 2
    found = [f.key for f in features if f.key.startswith(TEST_FEATURE)]
    assert f'{TEST_FEATURE}_fourth' in found
    assert f'{TEST_FEATURE}_fifth' in found


def test_can_remove_feature(backend: BaseBackend):
    remove_me = f'{TEST_FEATURE}_removeme'
    backend.add(remove_me)
    features = backend.features()
    assert remove_me in features
    backend.remove(remove_me)
    features = backend.features()
    assert remove_me not in features


def test_can_clear_feature(backend: BaseBackend):
    clear_me = f'{TEST_FEATURE}_clearme'
    backend.add(clear_me)
    backend.enable(clear_me, Gate.PercentageOfActors, 25)
    feature = backend.get(clear_me)
    assert feature.state == 'conditional'
    assert feature.percentage_of_actors_gate.value == 25
    backend.clear(clear_me)
    feature = backend.get(clear_me)
    assert feature.state == 'off'
    assert feature.percentage_of_actors_gate.value == None


def test_can_roll_out_to_actor(backend: BaseBackend):
    actor_me = f'{TEST_FEATURE}_actorme'
    backend.add(actor_me)
    assert (
        backend.get(actor_me)
        .actors_gate
        .is_open('yesactor', actor_me) == False
    )
    assert (
        backend.get(actor_me)
        .actors_gate
        .is_open('noactor', actor_me) == False
    )
    backend.enable(actor_me, Gate.Actors, 'yesactor')
    assert (
        backend.get(actor_me)
        .actors_gate
        .is_open('yesactor', actor_me) == True
    )
    assert (
        backend.get(actor_me)
        .actors_gate
        .is_open('noactor', actor_me) == False
    )


def test_can_roll_out_to_group(backend: BaseBackend):
    group_me = f'{TEST_FEATURE}_groupme'
    backend.add(group_me)
    assert (
        backend.get(group_me)
        .groups_gate
        .is_open('yesgroup', group_me) == False
    )
    assert (
        backend.get(group_me)
        .groups_gate
        .is_open('nogroup', group_me) == False
    )
    backend.enable(group_me, Gate.Groups, 'yesgroup')
    assert (
        backend.get(group_me)
        .groups_gate
        .is_open('yesgroup', group_me) == True
    )
    assert (
        backend.get(group_me)
        .groups_gate
        .is_open('nogroup', group_me) == False
    )


def test_can_roll_out_by_percent_actor(backend: BaseBackend):
    roll_me_out = f'{TEST_FEATURE}_rollmeout'
    backend.add(roll_me_out)
    assert (
        backend.get(roll_me_out)
        .percentage_of_actors_gate
        .is_open('anyactor', roll_me_out) == False
    )
    for percentage in [1, 10, 50, 25, 75, 100]:
        backend.enable(roll_me_out, Gate.PercentageOfActors, percentage)
        assert backend.get(roll_me_out).percentage_of_actors_gate.value == percentage

    # now we should be at 100%
    assert (
        backend.get(roll_me_out)
        .percentage_of_actors_gate
        .is_open('anyactor', roll_me_out) == True
    )


def test_to_json(backend: BaseBackend):
    json_me_1 = f'{TEST_FEATURE}_jsonme1'
    json_me_2 = f'{TEST_FEATURE}_jsonme2'
    backend.add(json_me_1)
    backend.add(json_me_2)
    backend.enable(json_me_1, Gate.Boolean)
    backend.enable(json_me_2, Gate.Actors, 'user1')
    backend.enable(json_me_2, Gate.Groups, 'group1')
    backend.enable(json_me_2, Gate.PercentageOfActors, 25)
    
    assert backend.to_json() == '{"django_flippy_testcase_jsonme1":{"key":"django_flippy_testcase_jsonme1","state":"on","gates":[{"key":"boolean","name":"boolean","value":true},{"key":"actors","name":"actor","value":[]},{"key":"groups","name":"group","value":[]},{"key":"percentage_of_actors","name":"percentage_of_actors","value":null},{"key":"percentage_of_time","name":"percentage_of_time","value":null},{"key":"expression","name":"expression","value":null}]},"django_flippy_testcase_jsonme2":{"key":"django_flippy_testcase_jsonme2","state":"conditional","gates":[{"key":"boolean","name":"boolean","value":null},{"key":"actors","name":"actor","value":["user1"]},{"key":"groups","name":"group","value":["group1"]},{"key":"percentage_of_actors","name":"percentage_of_actors","value":"25"},{"key":"percentage_of_time","name":"percentage_of_time","value":null},{"key":"expression","name":"expression","value":null}]}}'
