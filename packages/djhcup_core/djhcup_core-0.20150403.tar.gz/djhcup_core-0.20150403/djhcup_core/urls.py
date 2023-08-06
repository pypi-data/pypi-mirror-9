# Django imports
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# local imports
import utils
import views


# base patterns always available through having djhcup_core installed
urlpatterns = patterns('',
    url(r'^$', views.Index.as_view(), name='djhcup_core|index'),
    url(r'^login/$', 'djhcup_core.views.login', name='login'),
    url(r'^logout/$', 'djhcup_core.views.logout', name='logout'),
    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^activate/$', views.Activate.as_view(), name='activate'),
    url(r'^forgot-password/$', 'djhcup_core.views.forgot_password', name='forgot_password'),
	url(r'^password-reset-requested/$', TemplateView.as_view(template_name='password_reset_requested.html'), name='password_reset_requested'),
	url(r'^reset-password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'djhcup_core.views.reset_password', name='reset_password'),
	url(r'^reset-password-done/$', 'djhcup_core.views.reset_password_done', name='reset_password_done')
)


# check for installed modules, and include url patterns from each
installed_mods = utils.installed_modules()


# tack on url patterns for installed component modules
# these are always prefixed by the module name e.g. /staging/batches/
for mod, installed in installed_mods.iteritems():
    
    # but don't add core urls (this file) again
    if installed is True and mod not in ['djhcup_core']:
        prefix = mod.split('_')[-1]
        urlpatterns += patterns('',
                                url(r'^%s/' % prefix, include('%s.urls' % mod)),
                                )
