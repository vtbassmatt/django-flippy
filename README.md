# django-flippy

A [Flipper Cloud](https://www.flippercloud.io/) package for Django apps.
(Not affiliated with the Flipper Cloud folks, just think they're a good idea.)
Feature flags for Django projects, because why should the Rails people have all the fun?

## Installation

```ShellSession
# pip install django-flippy
```

Next open `settings.py`.
You need to add Flippy to your installed apps, middleware, and template context processors.

```python
# settings.py

INSTALLED_APPS = [
    ...,
    'flippy', # <-- the app
]

MIDDLEWARE = [
    ...,
    'flippy.middleware.flippy_middleware', # <-- the middleware
]

TEMPLATES = [
    {
        ...,
        'OPTIONS': {
            'context_processors': [
                ...,
                'flippy.context.processor',  # <-- the context processor
            ],
        },
    },
]
```

Finally, `./manage.py migrate` to run the migrations.

## Usage

### Raw, end-to-end example

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

### In a view

```python
# views.py
def index(request):
    if request.flippy.feature_exists('my_cool_feature')
        user_has_feature = request.flippy.is_enabled('my_cool_feature', request.user)

    if user_has_feature:
      return render(request, 'cool_new_feature_index.html')

    return render(request, 'index.html')
```

### In a template

```python
# views.py
def index(request):
  return render(request, 'index.html')
```

```html
<!-- index.html, abridged -->
{% if flippy.my_cool_feature.for_user %}
<p>You have access to the cool new feature!</p>
{% else %}
<p>Nothing new to see here.</p>
{% endif %}
```

## Using Flipper Cloud

The above recipes only use the local Django-based backend and does not connect you to
Flipper Cloud. There is a `FlipperCloudBackend` which expects a Flipper Cloud token
passed in the constructor. Be warned: this backend makes direct API calls for every
operation.

The better way to use Flipper Cloud is to set yourself up to use the Django backend.
Then run this periodically:

```ShellSession
FLIPPER_CLOUD_TOKEN=mytoken python manage.py sync-from-cloud
```

That will sync your Flipper Cloud data down to your local Django backend.

### The raw way

```python
from flippy import Flippy
from flippy.backends import FlipperCloudBackend

f = Flippy(FlipperCloudBackend('MY-TOKEN-HERE'))
```

### Using settings.py

In addition to the setup you did for Installation, add the following to your `settings.py`:

```python
# settings.py

FLIPPY_BACKEND = 'flippy.backends.FlipperCloudBackend'
FLIPPY_ARGS = ['MY-TOKEN-HERE']
```

This will configure the Flipper Cloud backend everywhere, including the middleware (`request.flippy`) and context processor (`{% if flippy.foo.for_user %}`).

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
