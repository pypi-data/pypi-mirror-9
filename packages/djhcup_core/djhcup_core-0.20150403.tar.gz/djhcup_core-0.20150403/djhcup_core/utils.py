# core Python packages
import importlib
import string
from random import choice


# django imports
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

# third party imports
import psycopg2


def installed_modules():
    """Check for installed modules and return list with relevant data
    """
    # detect presence/absence of component modules
    module_names = [
        'djhcup_core',
        'djhcup_staging',
        'djhcup_integration',
        'djhcup_reporting',
    ]
    installed = {}

    for x in module_names:
        # TODO: Rewrite to pull version numbers for each of these as well
        try:
            module = importlib.import_module(x)
            installed[x] = True
        except ImportError:
            installed[x] = False
    
    if len(installed) > 0:
        return installed
    else:
        return False


def get_pgcnxn(read_only=False):
    DB_DEF = settings.DATABASES['djhcup']
    cnxn = psycopg2.connect(
        host=DB_DEF['HOST'],
        port=DB_DEF['PORT'],
        user=DB_DEF['USER'],
        password=DB_DEF['PASSWORD'],
        database=DB_DEF['NAME'],
        )
    return cnxn


SALT_CHOICES = string.lowercase + string.digits
def salt(length=20, choices=SALT_CHOICES):
    return "".join(choice(choices) for n in xrange(length))

def make_html_email(html_body, *args, **kwargs):
    text_body = kwargs.pop('text_body', None)
    if not text_body:
        text_body = strip_tags(html_body)
    kwargs['body'] = text_body
    em = EmailMultiAlternatives(*args, **kwargs)
    em.attach_alternative(html_body, 'text/html')
    return em