# django-flippy

A [Flipper Cloud](https://www.flippercloud.io/) package for Django apps.

## Testing

We test with `pytest`.
By default, tests which require an active Flipper Cloud account aren't run.
You can run them with `pytest -m flippercloud`.
Note that you must set `FLIPPER_CLOUD_TOKEN` in your environment for them to run.
