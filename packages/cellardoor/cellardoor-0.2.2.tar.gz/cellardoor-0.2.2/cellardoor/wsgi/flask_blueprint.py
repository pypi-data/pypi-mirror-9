from flask import request
from flask.views import MethodView
import logging
import inspect
from ..api.methods import LIST, CREATE, GET, REPLACE, UPDATE, DELETE, get_http_methods
from ..serializers import JSONSerializer, MsgPackSerializer
from ..views import View
from ..views.minimal import MinimalView
from .. import errors

__all__ = ['add_to_falcon']


class Resource(MethodView):
	"""
	A resource exposes an interface through falcon
	"""
	
	# The types of content that are accepted.
	accept_serializers = (JSONSerializer(), MsgPackSerializer())
	params_serializer = JSONSerializer()
	
	
	def __init__(self, interface, views):
		self.interface = interface
		self.views = views
		self.logger = logging.getLogger(__name__)
		
		
	def get(self, id):
		pass
		
		
	def post(self):
		pass
		
		
	def put(self, id):
		pass
		
		
	def delete(self, id):
		pass
		
		
	def head(self):
		pass
		
		
class LinkResource(MethodView):
	
	def __init__(self, interface, link):
		self.interface = interface
		self.link = link
		
		
	def get(self):
		pass
		
		
	def head(self):
		pass


def flask_blueprint(api, name='api', views=(MinimalView,)):
	blueprint = Blueprint(name)
	
	views_by_type = []
	
	for v in views:
		if inspect.isclass(v):
			v = v()
		for mimetype, _ in v.serializers:
			views_by_type.append((mimetype, v))
	
	for interface in api.interfaces.values():
		resource_view = Resource.as_view(interface.plural_name, interface, views)
		blueprint.add_url_rule(
			'/%s/' % interface.plural_name,
			defaults={'id':None},
			view_func=resource_view,
			methods=['GET']
		)
		blueprint.add_url_rule(
			'/%s/' % interface.plural_name,
			view_func=resource_view,
			methods=['HEAD']
		)
		blueprint.add_url_rule(
			'/%s/' % interface.plural_name,
			view_func=resource_view,
			methods=['POST']
		)
		blueprint.add_url_rule(
			'/%s/<id>' % interface.plural_name,
			view_func=resource_view,
			methods=['GET', 'PUT', 'DELETE']
		)
		for link_name, link in interface.entity.get_links().items():
			if self.interface.api.get_interface_for_entity(link.entity):
				link_view = LinkResource.as_view('%s-%s' % (interface.plural_name, link_name), interface, link)
				blueprint.add_url_rule(
					'/%s/<id>/%s' % (interface.plural_name, link_name),
					view_func=link_view,
					methods=['GET', 'HEAD']
				)
	
	return blueprint