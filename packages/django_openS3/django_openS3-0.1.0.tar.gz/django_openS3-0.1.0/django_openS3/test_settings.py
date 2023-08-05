import os

TEST_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tests')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'django_openS3',
]

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(TEST_DIR, 'static'),
)


SECRET_KEY = "iufoj=mibkpjiugswsj8g5g4v8gg45k36kjcg76&-y5=!"

MIDDLEWARE_CLASSES = []

AWS_STORAGE_BUCKET_NAME = os.environ['AWS_S3_BUCKET']
AWS_ACCESS_KEY_ID = os.environ['AWS_S3_ACCESS_KEY']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_S3_SECRET_KEY']

DEFAULT_FILE_STORAGE = 'django_openS3.storage.S3MediaStorage'
STATICFILES_STORAGE = 'django_openS3.storage.S3StaticStorage'