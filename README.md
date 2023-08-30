# django-flippy

A [Flipper Cloud](https://www.flippercloud.io/) package for Django apps.
(Not affiliated with the Flipper Cloud folks, just think they're a good idea.)
Feature flags for Django projects, because why should the Rails people have all the fun?

## Installation

```ShellSession
# pip install django-flippy
```

Then add `flippy` to your `INSTALLED_APPS` in `settings.py`.
Finally, `./manage.py migrate` to run the migrations.

## Usage

```python
from django.contrib.auth.models import User

from flippy import Flippy
from flippy.backends import DjangoBackend

f = Flippy(DjangoBackend())

# create a feature
f.create('my_cool_feature')

# enable for half of all users
f.enable_percentage_of_actors('my_cool_feature', 50)

# check if a given user should get the feature
# (depending on chance, the user may or may not be flagged in -- if so,
# crank the percentage_of_actors up to 100 if you want to confirm it worked)
u = User.objects.get(pk=1)
if f.is_enabled('my_cool_feature', u):
  print('This user gets the cool new feature.')
else:
  print('This user gets the old, less cool feature.')
```

## Using Flipper Cloud

The above recipe only uses the local Django-based backend and does not connect you to
Flipper Cloud. There is a `FlipperCloudBackend` which expects a Flipper Cloud token
passed in the constructor:

```python
from flippy import Flippy
from flippy.backends import FlipperCloudBackend

f = Flippy(FlipperCloudBackend('MY-TOKEN-HERE'))
```

but be warned: this backend makes direct API calls for every operation. There will
be work to make Flipper Cloud a viable backend without having to make an HTTP request
for every operation, coming soon.

Other improvements will include ways to easily access these features from views,
templates, etc.

## Testing

We test with `pytest`.
By default, tests which require an active Flipper Cloud account aren't run.
You can run them with `pytest -m flippercloud`.
Note that you must set `FLIPPER_CLOUD_TOKEN` in your environment for them to run.

### Creating and testing a new backend

You may want to store your feature data differently. You can model your backend
off of `flippy.backends.MemoryBackend`, extending `flippy.core.BaseBackend` and
implementing all the methods. That interface is how `Flippy` (the user side) will
expect to interact with you. You can take a look at `tests/memory_backend_test.py`
to see how to run a suite of tests against your implementation.
