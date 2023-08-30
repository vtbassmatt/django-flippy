SECRET_KEY = "fake-key"
INSTALLED_APPS = [
    "flippy",
    "tests",
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
USE_TZ = True
