SECRET_KEY = 'test'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'src.modules.lms',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
USE_TZ = True
ROOT_URLCONF = 'src.modules.lms.tests.urls'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
