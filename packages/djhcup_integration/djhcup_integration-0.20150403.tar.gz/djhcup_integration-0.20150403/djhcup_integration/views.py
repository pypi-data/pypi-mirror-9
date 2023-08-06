# core Python packages
import logging


# third party packages


# django packages
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


# local imports


# start a logger
logger = logging.getLogger('default')


# Create your views here.

class Index(TemplateView):
	template_name = 'djhcup_base.html'

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(Index, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(Index, self).get_context_data(**kwargs)
		context['title'] = 'The Django-HCUP Hachoir: Integration Index'
		return context
