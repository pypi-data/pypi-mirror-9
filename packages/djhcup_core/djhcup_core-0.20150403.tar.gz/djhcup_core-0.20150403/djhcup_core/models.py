# Django imports
from django.db import models
from django.conf import settings

# local imports
import crypto

# Create your models here.

class UserProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	hcup_agreed = models.BooleanField(default=False)
	pudf_agreed = models.BooleanField(default=False)
	hcup_cert_code = models.CharField(max_length=32)
	activation_key = models.CharField(max_length=64, default=lambda: crypto.gen_random_hash())
