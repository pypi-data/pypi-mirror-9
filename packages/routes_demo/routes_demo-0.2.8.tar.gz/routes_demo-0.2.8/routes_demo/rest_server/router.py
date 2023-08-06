import routes
import routes.middleware
import webob.dec
import webob.exc

from routes_demo.rest_server import base
from routes_demo.rest_server import attributes
from routes_demo.plugins.pardnet.plugin import PardnetPlugin


RESOURCES = {'controller': 'controllers',
             'switch': 'switches',
             'haproxy': 'haproxies',
             'pool': 'pools',
             'vip': 'vips',
             'member': 'members',
             'health_monitor': 'health_monitors',}


COLLECTION_ACTIONS = ['index', 'create']
MEMBER_ACTIONS = ['show', 'update', 'delete']

REQUIREMENTS = {"""'id': attributes.UUID_PATTERN, """'format': 'xml|json'}

@webob.dec.wsgify
def index(req):
    return webob.Response("Hello World!")


@webob.dec.wsgify
def test(req):
    return webob.Response("test!")


class APIRouter(object):
    def __init__(self):
        self.mapper = routes.Mapper()
#         self.mapper.connect('/', controller=index, conditions={'method': ['GET']})
        self.mapper.connect('/test', controller=test, conditions={'method': ['GET']})
        plugin = PardnetPlugin("192.168.0.164", "9999")
        
        col_kwargs = dict(collection_actions=COLLECTION_ACTIONS,
                          member_actions=MEMBER_ACTIONS)
        
        
        def _map_resource(collection, resource, params, parent=None):
#             allow_bulk = cfg.CONF.allow_bulk
#             allow_pagination = cfg.CONF.allow_pagination
#             allow_sorting = cfg.CONF.allow_sorting
            controller = base.create_resource(
                collection, resource, plugin, params, #allow_bulk=allow_bulk,
                parent=parent, #allow_pagination=allow_pagination,
                #allow_sorting=allow_sorting
                )
            path_prefix = None
            if parent:
                path_prefix = "/%s/{%s_id}/%s" % (parent['collection_name'],
                                                  parent['member_name'],
                                                  collection)
            mapper_kwargs = dict(controller=controller,
                                 requirements=REQUIREMENTS,
                                 path_prefix=path_prefix,
                                 **col_kwargs)
            return self.mapper.collection(collection, resource,
                                     **mapper_kwargs)
        
#         mapper.connect('index', '/', controller=Index(RESOURCES))
        for resource in RESOURCES:
            _map_resource(RESOURCES[resource], resource,
                          attributes.RESOURCE_ATTRIBUTE_MAP.get(
                              RESOURCES[resource], dict()))
            
#         for resource in SUB_RESOURCES:
#             _map_resource(SUB_RESOURCES[resource]['collection_name'], resource,
#                           attributes.RESOURCE_ATTRIBUTE_MAP.get(
#                               SUB_RESOURCES[resource]['collection_name'],
#                               dict()),
#                           SUB_RESOURCES[resource]['parent'])
            
        self._router = routes.middleware.RoutesMiddleware(self._dispatch,
                                                          self.mapper)
    @webob.dec.wsgify
    def __call__(self, req):
        """Route the incoming request to a controller based on self.map.

        If no match, return a 404.
        """
        return self._router

    @staticmethod
    @webob.dec.wsgify
    def _dispatch(req):
        print req
        match = req.environ['wsgiorg.routing_args'][1]
        if not match:
            msg = 'The resource could not be found.'
            return webob.exc.HTTPNotFound(explanation=msg)
        app = match['controller']
        return app
        


