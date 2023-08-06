DEBUG = True

INSTALLED_APPS = [
    'adminextensions',
    'tests.app',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.sql',
    }
}

SECRET_KEY = 'Not very secret'

ROOT_URLCONF = 'tests.app.urls'

MIDDLEWARE_CLASSES = [
     'django.middleware.common.CommonMiddleware',
     'django.contrib.sessions.middleware.SessionMiddleware',
     'django.contrib.auth.middleware.AuthenticationMiddleware',
]
