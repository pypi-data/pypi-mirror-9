
import sqlalchemy as sa
from routes_demo.db import model_base
from routes_demo.db import models_v2

from routes_demo.common import uuidutils
from routes_demo.plugins.common import constants

from routes_demo.db.db_base_plugin import PardnetPluginBase
from routes_demo.db.common_db_mixin import CommonDbMixin





class Controller(model_base.BASEV2, models_v2.HasId, 
#                  models_v2.HasTenant,
                 models_v2.HasStatusDescription):
    """Represents a v2 neutron loadbalancer pool."""

    name = sa.Column(sa.String(255))
    description = sa.Column(sa.String(255))
    address = sa.Column(sa.String(64), nullable=False)
    username = sa.Column(sa.String(255), nullable=False)
    password = sa.Column(sa.String(255), nullable=False)
#     pool_id = sa.Column(sa.String(36), sa.ForeignKey("pools.id"),
#                          nullable=False)
    admin_state_up = sa.Column(sa.Boolean(), nullable=False)
    
    
class Switch(model_base.BASEV2, models_v2.HasId, 
#                  models_v2.HasTenant,
                 models_v2.HasStatusDescription):
    """Represents a v2 neutron loadbalancer pool."""
    
    __tablename__ = 'switches'
    name = sa.Column(sa.String(255))
    description = sa.Column(sa.String(255))
    address = sa.Column(sa.String(64), nullable=False)
#     username = sa.Column(sa.String(255), nullable=False)
#     password = sa.Column(sa.String(255), nullable=False)
    controller_id = sa.Column(sa.String(36), nullable=False)
    node_type = sa.Column(sa.String(36), nullable=False)
    dpid = sa.Column(sa.String(64), nullable=False)
    admin_state_up = sa.Column(sa.Boolean(), nullable=False)




class Haproxy(model_base.BASEV2, models_v2.HasId, 
#                  models_v2.HasTenant,
                 models_v2.HasStatusDescription):
    """Represents a v2 neutron loadbalancer pool."""

    __tablename__ = 'haproxies'
    name = sa.Column(sa.String(255))
    description = sa.Column(sa.String(255))
    address = sa.Column(sa.String(64), nullable=False)
    admin_state_up = sa.Column(sa.Boolean(), nullable=False)
    

class Flow(model_base.BASEV2, models_v2.HasId):
    """Represents a v2 neutron loadbalancer pool."""

    __tablename__ = 'flows'
    name = sa.Column(sa.String(255))
    node_type = sa.Column(sa.String(45), nullable=False)
    dpid = sa.Column(sa.String(45), nullable=False)
    priority = sa.Column(sa.String(45), nullable=False)
    ingress_port = sa.Column(sa.String(45), nullable=False)
    ether_type = sa.Column(sa.String(45), nullable=False)
    vlan_id = sa.Column(sa.String(45), nullable=False)
    vlan_priority = sa.Column(sa.String(45), nullable=False)
    actions = sa.Column(sa.String(45), nullable=False)
    installInHw = sa.Column(sa.String(45), nullable=False)
    protocol = sa.Column(sa.String(45), nullable=False)
    dl_dst = sa.Column(sa.String(45), nullable=False)
    dl_src = sa.Column(sa.String(45), nullable=False)
    nw_dst = sa.Column(sa.String(45), nullable=False)
    nw_src = sa.Column(sa.String(45), nullable=False)



class PardnetPluginDb(PardnetPluginBase, CommonDbMixin):
    
    def update_status(self, context, model, id, status,
                      status_description=None):
        with context.session.begin(subtransactions=True):
            v_db = self._get_resource(context, model, id)
            if v_db.status != status:
                v_db.status = status
            # update status_description in two cases:
            # - new value is passed
            # - old value is not None (needs to be updated anyway)
            if status_description or v_db['status_description']:
                v_db.status_description = status_description
    
    def _get_resource(self, context, model, id):
        r = self._get_by_id(context, model, id)
        return r
#         try:
#             r = self._get_by_id(context, model, id)
#         except exc.NoResultFound:
#             with excutils.save_and_reraise_exception(reraise=False) as ctx:
#                 if issubclass(model, Vip):
#                     raise loadbalancer.VipNotFound(vip_id=id)
#                 elif issubclass(model, Pool):
#                     raise loadbalancer.PoolNotFound(pool_id=id)
#                 elif issubclass(model, Member):
#                     raise loadbalancer.MemberNotFound(member_id=id)
#                 elif issubclass(model, HealthMonitor):
#                     raise loadbalancer.HealthMonitorNotFound(monitor_id=id)
#                 ctx.reraise = True
#         return r
    
    
    def _make_controller_dict(self, controller, fields=None):
        res = {'id': controller['id'],
#                'tenant_id': controller['tenant_id'],
               'name': controller['name'],
               'description': controller['description'],
               'address': controller['address'],
               'username': controller['username'],
               'password': controller['password'],
#                'pool_id': controller['pool_id'],
               'admin_state_up': controller['admin_state_up'],
               'status': controller['status'],
               'status_description': controller['status_description']
               }
        return self._fields(res, fields)
    
    def get_controllers(self, context, filters=None, fields=None):
        collection = self._model_query(context, Controller)
        collection = self._apply_filters_to_query(collection, Controller, filters)
        result = [self._make_controller_dict(c, fields)
                for c in collection]
        return result
    
    def get_controller(self, context, controller_id, fields=None):
        controller = self._get_resource(context, Controller, controller_id)
        return self._make_controller_dict(controller, fields)
    
    def create_controller(self, context, controller):
        v = controller['controller']

#         tenant_id = self._get_tenant_id_for_create(context, v)
        with context.session.begin(subtransactions=True):
            controller_db = Controller(id=uuidutils.generate_uuid(),
#                                        tenant_id=tenant_id,
                                       name=v['name'],
                                       description=v['description'],
                                       address=v['address'],
                                       username=v['username'],
                                       password=v['password'],
#                                        pool_id=v['pool_id'],
                                       admin_state_up=v['admin_state_up'],
                                       status=constants.PENDING_CREATE)
            context.session.add(controller_db)
        
#         status = constants.ACTIVE
#         self.update_status(context, Controller,
#                                   v["id"], status)

        return self._make_controller_dict(controller_db)

#     def assert_modification_allowed(self, obj):
#         status = getattr(obj, 'status', None)
# 
#         if status == constants.PENDING_DELETE:
#             raise loadbalancer.StateInvalid(id=id, state=status)

    def update_controller(self, context, id, controller):
        c = controller['controller']
        with context.session.begin(subtransactions=True):
            controller_db = self._get_resource(context, Controller, id)
#             self.assert_modification_allowed(controller_db)
            if c:
                controller_db.update(c)

        return self._make_controller_dict(controller_db)
    
    def delete_controller(self, context, controller_id):
        # Check if the pool is in use
#         self._ensure_controller_delete_conditions(context, controller_id)

        with context.session.begin(subtransactions=True):
            controller_db = self._get_resource(context, Controller, controller_id)
            context.session.delete(controller_db)
    

    def _make_switch_dict(self, switch, fields=None):
        res = {'id': switch['id'],
#                'tenant_id': controller['tenant_id'],
               'name': switch['name'],
               'description': switch['description'],
               'address': switch['address'],
               'controller_id': switch['controller_id'],
               'node_type': switch['node_type'],
               'dpid': switch['dpid'],
               'admin_state_up': switch['admin_state_up'],
               'status': switch['status'],
               'status_description': switch['status_description']
               }
        return self._fields(res, fields)


    def get_switches(self, context, filters=None, fields=None):
        collection = self._model_query(context, Switch)
        collection = self._apply_filters_to_query(collection, Switch, filters)
        result = [self._make_switch_dict(c, fields)
                for c in collection]
        return result

    
    def get_switch(self, context, switch_id, fields=None):
        switch = self._get_resource(context, Switch, switch_id)
        return self._make_switch_dict(switch, fields)


    def create_switch(self, context, switch):
        s = switch['switch']

#         tenant_id = self._get_tenant_id_for_create(context, v)
        with context.session.begin(subtransactions=True):
            switch_db = Switch(id=uuidutils.generate_uuid(),
#                                        tenant_id=tenant_id,
                                       name=s['name'],
                                       description=s['description'],
                                       address=s['address'],
                                       controller_id=s['controller_id'],
                                       node_type=s['node_type'],
                                       dpid=s['dpid'],
                                       admin_state_up=s['admin_state_up'],
                                       status=constants.PENDING_CREATE)
            context.session.add(switch_db)
        
#         status = constants.ACTIVE
#         self.update_status(context, Controller,
#                                   v["id"], status)

        return self._make_switch_dict(switch_db)


    def update_switch(self, context, id, switch):
        s = switch['switch']
        with context.session.begin(subtransactions=True):
            switch_db = self._get_resource(context, Switch, id)
#             self.assert_modification_allowed(controller_db)
            if s:
                switch_db.update(s)

        return self._make_switch_dict(switch_db)
    
    def delete_switch(self, context, switch_id):
        # Check if the pool is in use
#         self._ensure_controller_delete_conditions(context, controller_id)

        with context.session.begin(subtransactions=True):
            switch_db = self._get_resource(context, Switch, switch_id)
            context.session.delete(switch_db)



    def _make_haproxy_dict(self, haproxy, fields=None):
        res = {'id': haproxy['id'],
#                'tenant_id': controller['tenant_id'],
               'name': haproxy['name'],
               'description': haproxy['description'],
               'address': haproxy['address'],
#                'pool_id': controller['pool_id'],
               'admin_state_up': haproxy['admin_state_up'],
               'status': haproxy['status'],
               'status_description': haproxy['status_description']
               }
        return self._fields(res, fields)
    
    def get_haproxies(self, context, filters=None, fields=None):
        collection = self._model_query(context, Haproxy)
        collection = self._apply_filters_to_query(collection, Haproxy, filters)
        result = [self._make_haproxy_dict(c, fields)
                for c in collection]
        return result
    
    def get_haproxy(self, context, haproxy_id, fields=None):
        haproxy = self._get_resource(context, Haproxy, haproxy_id)
        return self._make_haproxy_dict(haproxy, fields)


    def create_haproxy(self, context, haproxy):
        h = haproxy['haproxy']

#         tenant_id = self._get_tenant_id_for_create(context, v)
        with context.session.begin(subtransactions=True):
            haproxy_db = Haproxy(id=uuidutils.generate_uuid(),
#                                        tenant_id=tenant_id,
                                       name=h['name'],
                                       description=h['description'],
                                       address=h['address'],
#                                        pool_id=v['pool_id'],
                                       admin_state_up=h['admin_state_up'],
                                       status=constants.PENDING_CREATE)
            context.session.add(haproxy_db)
        
#         status = constants.ACTIVE
#         self.update_status(context, Controller,
#                                   v["id"], status)

        return self._make_haproxy_dict(haproxy_db)

#     def assert_modification_allowed(self, obj):
#         status = getattr(obj, 'status', None)
# 
#         if status == constants.PENDING_DELETE:
#             raise loadbalancer.StateInvalid(id=id, state=status)

    def update_haproxy(self, context, id, haproxy):
        h = haproxy['haproxy']
        with context.session.begin(subtransactions=True):
            haproxy_db = self._get_resource(context, Haproxy, id)
#             self.assert_modification_allowed(controller_db)
            if h:
                haproxy_db.update(h)

        return self._make_haproxy_dict(haproxy_db)
    
    def delete_haproxy(self, context, haproxy_id):
        # Check if the pool is in use
#         self._ensure_controller_delete_conditions(context, controller_id)

        with context.session.begin(subtransactions=True):
            haproxy_db = self._get_resource(context, Haproxy, haproxy_id)
            context.session.delete(haproxy_db)
            
            
            
    
    def _make_flow_dict(self, flow, fields=None):
        res = {'id': flow['id'],
               'name': flow['name'],
               'priority': flow['priority'],
               'actions': flow['actions'],
               'installInHw': flow['installInHw'],
               'dl_dst': flow['dl_dst'],
               'dl_src': flow['dl_src'],
               'nw_dst': flow['nw_dst'],
               'nw_src': flow['nw_src'],
               'protocol': flow['protocol'],
               'ether_type': flow['ether_type'],
               'dpid': flow['dpid'],
               'node_type': flow['node_type'],
               }
        return self._fields(res, fields)
    
    def get_flows(self, context, filters=None, fields=None):
        collection = self._model_query(context, Flow)
        collection = self._apply_filters_to_query(collection, Flow, filters)
        result = [self._make_flow_dict(c, fields)
                for c in collection]
        return result
    
    def get_flow(self, context, flow_id, fields=None):
        flow = self._get_resource(context, Flow, flow_id)
        return self._make_flow_dict(flow, fields)


    def create_flow(self, context, flow):
        f = flow
        actions = f['actions']
        action_string = ','.join(actions)
        with context.session.begin(subtransactions=True):
            flow_db = Flow(id=uuidutils.generate_uuid(),
                           name=f['name'],
                           priority=f['priority'],
                           actions=action_string,
                           installInHw=f['installInHw'],
                           dl_dst=f['dlDst'] if 'dlDst' in f else None,
                           dl_src=f['dlSrc'] if 'dlSrc' in f else None,
                           nw_dst=f['nwDst'] if 'nwDst' in f else None,
                           nw_src=f['nwSrc'] if 'nwSrc' in f else None,
                           protocol=f['protocol'] if 'protocol' in f else None,
                           ether_type=f['etherType'] if 'etherType' in f else None,
                           dpid=f['node']['id'],
                           node_type=f['node']['type'],
                           )
            context.session.add(flow_db)

        return self._make_flow_dict(flow_db)

#     def assert_modification_allowed(self, obj):
#         status = getattr(obj, 'status', None)
# 
#         if status == constants.PENDING_DELETE:
#             raise loadbalancer.StateInvalid(id=id, state=status)

    def update_flow(self, context, id, flow):
        f = flow['flow']
        with context.session.begin(subtransactions=True):
            flow_db = self._get_resource(context, Flow, id)
#             self.assert_modification_allowed(controller_db)
            if f:
                flow_db.update(f)

        return self._make_flow_dict(flow_db)
    
    def delete_flow(self, context, flow_id):
        # Check if the pool is in use
#         self._ensure_controller_delete_conditions(context, controller_id)

        with context.session.begin(subtransactions=True):
            flow_db = self._get_resource(context, Flow, flow_id)
            context.session.delete(flow_db)



