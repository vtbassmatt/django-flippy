import platform
import sys
from json.decoder import JSONDecodeError

import httpx

from flippy.backends import BaseBackend
from flippy.core import Feature, FeatureName, Gate
from flippy.exceptions import (FeatureNotFound, FlipperIdInvalid,
                               GroupNotRegistered, NameInvalid,
                               PercentageInvalid)

FLIPPER_CLOUD_BASE_URL = 'https://www.flippercloud.io/adapter'
SYSTEM_PLATFORM = f"{platform.machine() or 'unknown'}-{platform.system() or 'unknown'}"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': "django-flippy v0.0.1",
    "Client-Language": "python",
    "Client-Language-Version": sys.version,
    "Client-Platform": SYSTEM_PLATFORM,
    # TODO: others from https://github.com/flippercloud/flipper/blob/main/lib/flipper/adapters/http/client.rb
    # "Client-Engine": "",
    # "Client-Pid": Process.pid.to_s,
    # "Client-Thread": Thread.current.object_id.to_s,
    # "Client-Hostname": Socket.gethostname,
}


# As of 2023-08-26, there are many cases where Flipper Cloud responds
# with success even if the feature doesn't exist or nothing was changed.
# This makes many requests idempotent, but also makes it hard to surface
# problems to the consumer. 🤷

class FlipperCloudBackend(BaseBackend):
    """
    Get flags direct from Flipper Cloud.
    
    Note that this is not the preferred implementation, as it'll cause a service
    to service call on every invocation. However, it's good for scaffolding and
    kicking tires.
    """
    def __init__(self, token: str):
        if not token:
            raise ValueError('must pass a Flipper Cloud token')

        self.client = httpx.Client(
            base_url=FLIPPER_CLOUD_BASE_URL,
            headers=HEADERS | { "Flipper-Cloud-Token": token },
        )

    def features(self) -> set[FeatureName]:
        "Get the set of known features."
        r = self.client.get('/features?exclude_gate_names=true')
        self._raise_from_cloud(r)

        return {f['key'] for f in r.json()['features']}

    def add(self, feature: FeatureName) -> bool:
        "Add a feature to the set of known features."
        body = { 'name': feature }
        r = self.client.post('/features', json=body)
        self._raise_from_cloud(r, { 'feature': feature })
        return r.is_success

    def remove(self, feature: FeatureName) -> bool:
        "Remove a feature from the set of known features."
        r = self.client.delete(f'/features/{feature}')
        self._raise_from_cloud(r, { 'feature': feature })
        return r.is_success

    def clear(self, feature: FeatureName) -> bool:
        "Clear all gate values for a feature."
        r = self.client.delete(f'features/{feature}/clear')
        self._raise_from_cloud(r, { 'feature': feature })
        return r.is_success

    def get(self, feature: FeatureName) -> Feature:
        "Get all gate values for a feature."
        r = self.client.get(f'/features/{feature}')

        self._raise_from_cloud(r, { 'feature': feature })
        return Feature.from_api(r.json())        

    def enable(self, feature: FeatureName, gate: Gate, thing: str | int | None=None) -> bool:
        "Enable a gate for a thing."
        body = self._body_for_gate(gate, thing)
        qs = { 'allow_unregistered_groups': 'true' } if gate == Gate.Groups else {}
        r = self.client.post(
            f'/features/{feature}/{gate.value}',
            json=body,
            params=qs,
        )
        
        self._raise_from_cloud(r, { 'feature': feature })
        return r.is_success

    def disable(self, feature: FeatureName, gate: Gate, thing: str | int | None=None) -> bool:
        "Disable a gate for a thing."
        body = self._body_for_gate(gate, thing)
        qs = { 'allow_unregistered_groups': 'true' } if gate == Gate.Groups else {}
        # httpx doesn't accept `json` on .delete(), but the body is a required part
        # of some disable requests
        req = self.client.build_request(
            'DELETE',
            f'/features/{feature}/{gate.value}',
            json=body,
            params=qs,
        )
        r = self.client.send(req)
        self._raise_from_cloud(r, { 'feature': feature })

        return r.is_success

    def get_multi(self, features: list[FeatureName]) -> list[Feature]:
        "Get all gate values for several features at once."
        qs = {
            'exclude_gate_names': 'true',
            'keys': ','.join(features),
        }
        r = self.client.get('/features', params=qs)
        self._raise_from_cloud(r)

        return [Feature.from_api(f) for f in r.json()['features']]

    def get_all(self) -> list[Feature]:
        "Get all gate values for all features at once."
        qs = {
            'exclude_gate_names': 'true',
        }
        r = self.client.get('/features', params=qs)
        self._raise_from_cloud(r)

        return [Feature.from_api(f) for f in r.json()['features']]

    def _body_for_gate(self, gate: Gate, thing: str | int | None) -> dict:
        match gate:
            case Gate.Boolean:
                return {}
            case Gate.Actors:
                return { 'flipper_id': str(thing) }
            case Gate.Groups:
                return { 'name': str(thing) }
            case Gate.PercentageOfActors | Gate.PercentageOfTime:
                return { 'percentage': str(thing) }
            case Gate.Expression:
                raise NotImplementedError("ExpressionGate isn't supported")
            case _:
                raise ValueError(f"{gate} is not a known gate type")

    def _raise_from_cloud(self, response: httpx.Response, extra: dict = {}):
        # https://www.flippercloud.io/docs/api#error-code-reference
        if response.is_client_error or response.is_success:
            try:
                result = response.json()
            except JSONDecodeError:
                result = {}
            if 'code' not in result:
                return
            
            match result['code']:
                case 1:
                    raise FeatureNotFound(extra.get('feature', ''))
                case 2:
                    raise GroupNotRegistered(result.get('message', ''))
                case 3:
                    raise PercentageInvalid(result.get('message', ''))
                case 4:
                    raise FlipperIdInvalid(result.get('message', ''))
                case 5:
                    raise NameInvalid(result.get('message', ''))

        response.raise_for_status()

    def to_json(self) -> str:
        "Produce a JSON-formatted string containing state for all features."
        return super().to_json()

    def from_json(self, new_state: str) -> None:
        "Clear current state and replace with state from a JSON-formatted string."
        raise NotImplementedError()
