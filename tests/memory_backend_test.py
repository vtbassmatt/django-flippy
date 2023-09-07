import pytest

from flippy.backends import BaseBackend, MemoryBackend
from tests.backend_shared import *


@pytest.fixture
def backend() -> BaseBackend:
    return MemoryBackend()


# TODO: move to shared once others are implemented
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


def test_from_json(backend: BaseBackend):
    backend.from_json('{"django_flippy_testcase_unjsonme1":{"key":"django_flippy_testcase_unjsonme1","state":"on","gates":[{"key":"boolean","name":"boolean","value":true},{"key":"actors","name":"actor","value":[]},{"key":"groups","name":"group","value":[]},{"key":"percentage_of_actors","name":"percentage_of_actors","value":null},{"key":"percentage_of_time","name":"percentage_of_time","value":null},{"key":"expression","name":"expression","value":null}]},"django_flippy_testcase_unjsonme2":{"key":"django_flippy_testcase_unjsonme2","state":"conditional","gates":[{"key":"boolean","name":"boolean","value":null},{"key":"actors","name":"actor","value":["user1"]},{"key":"groups","name":"group","value":["group1"]},{"key":"percentage_of_actors","name":"percentage_of_actors","value":"25"},{"key":"percentage_of_time","name":"percentage_of_time","value":null},{"key":"expression","name":"expression","value":null}]}}')

    unjson_me_1 = f'{TEST_FEATURE}_unjsonme1'
    unjson_me_2 = f'{TEST_FEATURE}_unjsonme2'

    assert backend.get(unjson_me_1).state == 'on'

    feat = backend.get(unjson_me_2)
    assert feat.actors_gate.value == ['user1']
    assert feat.groups_gate.value == ['group1']
    assert feat.percentage_of_actors_gate.value == 25
