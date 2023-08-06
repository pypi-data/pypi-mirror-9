# Django imports

from django import forms
from django.contrib.auth.forms import UserCreationForm

# Local imports
from models import UserProfile

class RegistrationForm(UserCreationForm):
	class Meta(UserCreationForm.Meta):
		fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

	error_messages = dict(UserCreationForm.error_messages.items() + {
		'non_umhs_email': 'Only @med.umich.edu email addresses are allowed at this time.'
	}.items())

	hcup_agreed = forms.BooleanField(required=True)
	hcup_cert_code = forms.CharField()
	pudf_agreed = forms.BooleanField(required=True)

	def clean_email(self):
		email = self.cleaned_data['email']
		if email:
			if not email.endswith('med.umich.edu'):
				raise forms.ValidationError(self.error_messages['non_umhs_email'], code='non_umhs_email')
		return email

	def save(self, commit=True):
		user = super(RegistrationForm, self).save(commit=False)
		user.is_active = False
		if commit:
			user.save()
			profile, created = UserProfile.objects.get_or_create(user=user)
			profile.hcup_agreed = self.cleaned_data['hcup_agreed']
			profile.pudf_agreed = self.cleaned_data['pudf_agreed']
			profile.hcup_cert_code = self.cleaned_data['hcup_cert_code']
			profile.save()
			return (user, profile)
		return (user, None)

