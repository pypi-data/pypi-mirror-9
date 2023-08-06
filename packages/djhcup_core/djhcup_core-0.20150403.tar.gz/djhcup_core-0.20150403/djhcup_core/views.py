# core Python packages
import logging


# third party packages


# django packages
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.core.urlresolvers import reverse
from django.utils.timezone import utc
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import django.contrib.auth.views as auth_views
from django.contrib.sites.models import RequestSite
from django.views.generic import View, FormView, TemplateView
from django.template.loader import render_to_string

# local imports
from utils import installed_modules, make_html_email
from forms import RegistrationForm
from models import UserProfile

# start a logger
logger = logging.getLogger('default')

class Index(TemplateView):
    template_name = 'djhcup_core_index.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Index, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['title'] = 'The Django-HCUP Hachoir: Core Index'
        return context

def login(request):
    return auth_views.login(request, template_name='login.html', extra_context={
        'title': 'Login'
    })

def logout(request):
    return auth_views.logout_then_login(request)

class Register(FormView):
    form_class = RegistrationForm
    template_name = 'register.html'

    def form_valid(self, form):
        user, profile = form.save()
        email_body = render_to_string('email_activation.html', {
            'site': RequestSite(self.request),
            'user': user,
            'profile': profile
        })
        em = make_html_email(email_body, subject="Activate your account", to=[user.email])
        em.send()
        messages.info(self.request, 'An email with instructions for activating your account has been sent to the email address you provided.')
        return super(Register, self).form_valid(form)

    def get_success_url(self):
        return reverse('login')

    def get_context_data(self, **kwargs):
        context = super(Register, self).get_context_data(**kwargs)
        context['title'] = 'Register'
        return context

class Activate(View):
    def get(self, request, *args, **kwargs):
        ak = request.GET.get('key')
        try:
            profile = UserProfile.objects.exclude(user__is_active=True).exclude(activation_key__iexact='ACTIVATED').get(activation_key=ak)
        except UserProfile.DoesNotExist:
            messages.error(request, 'Invalid activation key.')
            return redirect('login')
        user = profile.user
        user.is_active = True
        user.save(update_fields=['is_active'])
        profile.activation_key = 'ACTIVATED'
        profile.save(update_fields=['activation_key'])
        messages.success(request, 'Account activated! You may now log in.')
        return redirect('login')

def forgot_password(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    return auth_views.password_reset(request, template_name='forgot_password.html', email_template_name='email_reset_password.html',
        extra_context={'title': 'Forgot your password?'}, post_reset_redirect=reverse('password_reset_requested'))

def reset_password(request, *args, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    return auth_views.password_reset_confirm(request, *args, template_name='reset_password.html', post_reset_redirect=reverse('reset_password_done'), **kwargs)

def reset_password_done(request):
    messages.success(request, 'Password reset succcessfully. You may now log in.')
    return redirect('login')

