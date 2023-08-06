import os

from django.utils import six


BASE_DIR = os.path.dirname(__file__)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'crispy_forms',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

ROOT_URLCONF = 'urls'
CRISPY_CLASS_CONVERTERS = {"textinput": "textinput textInput inputtext"}
SECRET_KEY = 'secretkey'
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))


# http://djangosnippets.org/snippets/646/
class InvalidVarException(object):
    def __mod__(self, missing):
        try:
            missing_str = six.text_type(missing)
        except:
            missing_str = 'Failed to create string representation'
        raise Exception('Unknown template variable %r %s' % (missing, missing_str))

    def __contains__(self, search):
        if search == '%s':
            return True
        return False


# Vintage template settings.
TEMPLATE_DEBUG = True
TEMPLATE_STRING_IF_INVALID = InvalidVarException()


# Modern template settings.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': True,
            'string_if_invalid': InvalidVarException(),
        },
    },
]
