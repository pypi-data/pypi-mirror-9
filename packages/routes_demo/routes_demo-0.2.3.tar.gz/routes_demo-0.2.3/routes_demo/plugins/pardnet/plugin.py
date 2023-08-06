from routes_demo.db.pardnet_db import PardnetPluginDb


import requests
import base64
import json
from oslo.serialization import jsonutils
from math import log

import os
import platform
import re




CONTENT_TYPE_HEADER = 'Content-type'
ACCEPT_HEADER = 'Accept'
AUTH_HEADER = 'Authorization'
DRIVER_HEADER = 'X-OpenStack-LBaaS'
TENANT_HEADER = 'X-Tenant-ID'
JSON_CONTENT_TYPE = 'application/json'


class PardnetPlugin(PardnetPluginDb):
    
    def __init__(self, pardnet_ip, pardnet_port):
        
        
        self.pardnet_uri = "http://%s:%s" % (pardnet_ip, pardnet_port)
        self.auth = None
        




    
    def get_controllers(self, context, filters=None, fields=None):
        session = context.session
        with session.begin(subtransactions=True):
            controllers = super(PardnetPlugin,
                                self).get_controllers(context, filters, None)
#             for controller in controllers:
#                 self.type_manager._extend_network_dict_provider(context, controller)

        return [self._fields(controller, fields) for controller in controllers]
#         return [{"id": "abc", "name": "jaff", "description": "description", "admin_state_up": "True",
#                  "address": "192.168.0.99", "username": "admin", "password": "admin", "status": "ACTIVE", "tenant_id": "abc"}]

    def get_controller(self, context, id, fields=None):
        session = context.session
        with session.begin(subtransactions=True):
            result = super(PardnetPlugin, self).get_controller(context, id, None)
#             self.type_manager._extend_network_dict_provider(context, result)

        return self._fields(result, fields)
    
    def create_controller(self, context, controller):
#         controller_data = controller['controller']
#         tenant_id = self._get_tenant_id_for_create(context, controller_data)
        session = context.session
        with session.begin(subtransactions=True):
#             self._ensure_default_security_group(context, tenant_id)
            result = super(PardnetPlugin, self).create_controller(context, controller)
#             self.extension_manager.process_create_network(session, net_data,
#                                                           result)
#             self._process_l3_create(context, result, net_data)
#             net_data['id'] = result['id']
#             self.type_manager.create_network_segments(context, net_data,
#                                                       tenant_id)
#             self.type_manager._extend_network_dict_provider(context, result)
#             mech_context = driver_context.NetworkContext(self, context,
#                                                          result)
#             self.mechanism_manager.create_network_precommit(mech_context)

#         try:
#             self.mechanism_manager.create_network_postcommit(mech_context)
#         except ml2_exc.MechanismDriverError:
#             with excutils.save_and_reraise_exception():
#                 LOG.error(_("mechanism_manager.create_network_postcommit "
#                             "failed, deleting network '%s'"), result['id'])
#                 self.delete_network(context, result['id'])
        return result

    def update_controller(self, context, id, controller):
        session = context.session
        with session.begin(subtransactions=True):
            result = super(PardnetPlugin, self).update_controller(context, id, controller)
        return result

    def delete_controller(self, context, id):
        session = context.session
        with session.begin(subtransactions=True):
            result = super(PardnetPlugin, self).delete_controller(context, id)
            
            
    def get_switches(self, context, filters=None, fields=None):
        session = context.session
        with session.begin(subtransactions=True):
            switches = super(PardnetPlugin,
                                self).get_switches(context, filters, None)
#             for controller in controllers:
#                 self.type_manager._extend_network_dict_provider(context, controller)

        return [self._fields(switch, fields) for switch in switches]
#         return [{"id": "abc", "name": "jaff", "description": "description", "admin_state_up": "True",
#                  "address": "192.168.0.99", "username": "admin", "password": "admin", "status": "ACTIVE", "tenant_id": "abc"}]

    def get_switch(self, context, id, fields=None):
        session = context.session
        with session.begin(subtransactions=True):
            result = super(PardnetPlugin, self).get_switch(context, id, None)
#             self.type_manager._extend_network_dict_provider(context, result)

        return self._fields(result, fields)
        
        
        
    def create_switch(self, context, switch):
#         controller_data = controller['controller']
#         tenant_id = self._get_tenant_id_for_create(context, controller_data)
        session = context.session
        with session.begin(subtransactions=True):
#             self._ensure_default_security_group(context, tenant_id)
            result = super(PardnetPlugin, self).create_switch(context, switch)
        return result
        
        
        
    def update_switch(self, context, id, switch):
        session = context.session
        with session.begin(subtransactions=True):
            result = super(PardnetPlugin, self).update_switch(context, id, switch)
        return result

    def delete_switch(self, context, id):
        session = context.session
        with session.begin(subtransactions=True):
            result = super(PardnetPlugin, self).delete_switch(context, id)
            
            
            
            
    def get_haproxies(self, context, filters=None, fields=None):
        session = context.session
        with session.begin(subtransactions=True):
            haproxies = super(PardnetPlugin,
                                self).get_haproxies(context, filters, None)
#             for controller in controllers:
#                 self.type_manager._extend_network_dict_provider(context, controller)

        return [self._fields(haproxy, fields) for haproxy in haproxies]
#         return [{"id": "abc", "name": "jaff", "description": "description", "admin_state_up": "True",
#                  "address": "192.168.0.99", "username": "admin", "password": "admin", "status": "ACTIVE", "tenant_id": "abc"}]

    def get_haproxy(self, context, id, fields=None):
        session = context.session
        with session.begin(subtransactions=True):
            result = super(PardnetPlugin, self).get_haproxy(context, id, None)
#             self.type_manager._extend_network_dict_provider(context, result)

        return self._fields(result, fields)
        
        
        
    def create_haproxy(self, context, haproxy):
#         controller_data = controller['controller']
#         tenant_id = self._get_tenant_id_for_create(context, controller_data)
        session = context.session
        with session.begin(subtransactions=True):
#             self._ensure_default_security_group(context, tenant_id)
            result = super(PardnetPlugin, self).create_haproxy(context, haproxy)
        return result
        
        
        
    def update_haproxy(self, context, id, haproxy):
        session = context.session
        with session.begin(subtransactions=True):
            result = super(PardnetPlugin, self).update_haproxy(context, id, haproxy)
        return result

    def delete_haproxy(self, context, id):
        session = context.session
        with session.begin(subtransactions=True):
            result = super(PardnetPlugin, self).delete_haproxy(context, id)
            
        
    def create_pool(self, context, pool):
#         session = context.session
#         with session.begin(subtransactions=True):
#             result = super(PardnetPlugin, self).create_haproxy(context, pool)
#         return result
        return {"pool": {}}
        
        
    def update_pool(self, context, id, pool):
#         session = context.session
#         with session.begin(subtransactions=True):
#             result = super(PardnetPlugin, self).update_haproxy(context, id, pool)
#         return result
        pass

    def delete_pool(self, context, id):
#         session = context.session
#         with session.begin(subtransactions=True):
#             result = super(PardnetPlugin, self).delete_haproxy(context, id)
        pass
            
            
            
    def create_vip(self, context, vip):
        
        
        
        
        
        session = context.session
        with session.begin(subtransactions=True):
            controllers = super(PardnetPlugin,
                                self).get_controllers(context)
            switches = super(PardnetPlugin,
                                self).get_switches(context)
                                
#             for controller in controllers:
#                 self.type_manager._extend_network_dict_provider(context, controller)

        controller = controllers[0]
        
        switch = switches[0]
        
        odl_uri = "http://%s:8080/%s" % (controller["address"], "controller/nb/v2/flowprogrammer/default")
        
        self.odl_flow_url = "%s/%s/%s/%s/%s" % (odl_uri, "node", switch["node_type"], switch["dpid"], "staticFlow")
        base64string = base64.encodestring("%s:%s" % (controller["username"], controller["password"]))
        base64string = base64string[:-1]
        """Authorization Header"""
        self.auth = 'Basic %s' % base64string
        
#         normal_name = "%s_normal" % vip["vip"]["address"].replace(".", "_")
#         self.remove_resource(self.odl_flow_url, normal_name)
        
        
        flow_dict = self._sourceip_flow_dict(context, vip["vip"]["address"])
        for key in flow_dict.keys():
            super(PardnetPlugin, self).create_flow(context, flow_dict[key])
            self.update_resource(self.odl_flow_url, key, None, json.dumps(flow_dict[key]))
        
        
        return {"vip": {}}
        
        
    def update_vip(self, context, id, vip):
        pass


    def delete_vip(self, context, vip):
        """add vip_normal flow"""
        
        
        session = context.session
        with session.begin(subtransactions=True):
            controllers = super(PardnetPlugin,
                                self).get_controllers(context)
            switches = super(PardnetPlugin,
                                self).get_switches(context)
                                
#             for controller in controllers:
#                 self.type_manager._extend_network_dict_provider(context, controller)

        controller = controllers[0]
        
        switch = switches[0]
        
        odl_uri = "http://%s:8080/%s" % (controller["address"], "controller/nb/v2/flowprogrammer/default")
        
        self.odl_flow_url = "%s/%s/%s/%s/%s" % (odl_uri, "node", switch["node_type"], switch["dpid"], "staticFlow")
        base64string = base64.encodestring("%s:%s" % (controller["username"], controller["password"]))
        base64string = base64string[:-1]
        """Authorization Header"""
        self.auth = 'Basic %s' % base64string
        
        vip = vip.replace("_", ".")
        vip_name = vip.replace(".", "_")
        filters = {'nwDst': vip}
        flows = super(PardnetPlugin, self).get_flows(context, filters)
        
        print flows
        for flow in flows:
            self.remove_resource(self.odl_flow_url, flow['name'])
            super(PardnetPlugin, self).delete_flow(context, flow['id'])
            
        
        
        
        
#         flow_name = "%s_normal" % vip_name
#         
#         flow_dict = self._create_flow_dict(flow_name,
#                                             switch["node_type"],
#                                             switch["dpid"],
#                                             "5000",
#                                             ["HW_PATH"],
#                                             True,
#                                             nwDst=vip,
#                                             etherType="0x800"
#                                             )
#         self.update_resource(self.odl_flow_url, flow_name, None, json.dumps(flow_dict))
    
            
    def create_member(self, context, member):
        return {"member": {}}
        
        
    def update_member(self, context, id, member):
        pass


    def delete_member(self, context, id):
        pass
    
    
    
            
    def create_health_monitor(self, context, health_monitor):
        return {"health_monitor": {}}
        
        
    def update_health_monitor(self, context, id, health_monitor):
        pass


    def delete_health_monitor(self, context, id):
        pass
    
    
    
    def _get_mac_by_ip(self, ip):
        sysstr = platform.system()
        if sysstr == 'Windows':
            macaddr = self.__forWin(ip)
        elif sysstr == 'Linux':
            macaddr = self.__forLinux(ip)
        else:
            macaddr = None
        return macaddr or '00-00-00-00-00-00'
    
    def __forWin(self, ip):
        patt_mac = re.compile('([a-f0-9]{2}[-:]){5}[a-f0-9]{2}', re.I)
        os.popen('ping -n 1 -w 500 {} > nul'.format(ip))
        macaddr = os.popen('arp -a {}'.format(ip))
        macaddr = patt_mac.search(macaddr.read())
        if macaddr:
            macaddr = macaddr.group()
        else:
            macaddr = None
        return macaddr

    def __forLinux(self, ip):
        patt_mac = re.compile('([a-f0-9]{2}[-:]){5}[a-f0-9]{2}', re.I)
        os.popen('ping -nq -c 1 -W 500 {} > /dev/null'.format(ip))
        result = os.popen('arp -an {}'.format(ip))
        result = patt_mac.search(result.read())
        return result.group() if result else None
    
    
    def _get_ofport(self):
        return "1"
    
    
    
    
    
    
    
    def _sourceip_flow_dict(self, context, vip):
        """return the flow dictionary with key of flow_name and value of flow_config dictionary"""
        return_dict = {}
        haproxies = self.get_haproxies(context)
        haproxy_num = len(haproxies)
        
        switches = self.get_switches(context)
        switch = switches[0]
        
        
        cidr_suffix = int(log(haproxy_num, 2)) + 1
        subnet_num = 2 ** (cidr_suffix)
        
        for i in range(subnet_num):
            index = i % haproxy_num
            actions = []
#             set_dl_dst = "SET_DL_DST=%s" % self.ha_info[index]["ha_mac"]
            set_dl_dst = "SET_DL_DST=%s" % self._get_mac_by_ip(haproxies[index]["address"])
#             output = "OUTPUT=%s" % self.ha_info[index]["ha_ofport"]
            output = "OUTPUT=%s" % self._get_ofport()
            actions.append(set_dl_dst)
            actions.append(output)
            
            if subnet_num <= 256:
                """if i == 0 , set address to 0"""
                source_ip = "%s.0.0.0/%s" % (str(i * (2 ** (8 - cidr_suffix))), cidr_suffix)
            
            flow_name = source_ip.replace("/", "_")
            return_dict[flow_name] = self._create_flow_dict(flow_name,
                                                            switch["node_type"],
                                                            switch["dpid"],
                                                            "500",
                                                            actions,
                                                            True,
                                                            nwSrc=source_ip,
                                                            nwDst=vip,
                                                            etherType="0x800"
                                                            )
            
            
        
#         for ip_host in self._sourceip_map_to_list():xxxxxxx
#             actions = []
#             set_dl_dst = "SET_DL_DST=%s" % self.ha_info[ip_host["dst_ha_name"]]["ha_mac"]
#             output = "OUTPUT=%s" % self.ha_info[ip_host["dst_ha_name"]]["ha_ofport"]
#             actions.append(set_dl_dst)
#             actions.append(output)
#              
#             flow_name = ip_host["source_ip"].replace("/", "_")
#             return_dict[flow_name] = self._create_flow_dict(flow_name,
#                                                             self.odl_switch_node_type,
#                                                             self.odl_switch_node_id,
#                                                             "500",
#                                                             actions,
#                                                             True,
#                                                             nwSrc=ip_host["source_ip"],
#                                                             nwDst=self.vip,
#                                                             etherType="0x800"
#                                                             )
        return return_dict
    
    



    def _create_flow_dict(self, name, node_type, node_id, priority, actions, installInHw=True, nwSrc=None, nwDst=None, etherType=None):
        """return a flow_config dictionary"""
        #return '{"priority":"0","hardTimeout":"0","actions":["DROP"],"node":{"id":"00:00:00:0c:29:d2:16:cf","type":"OF"},"installInHw":"true","name":"test"}'
        return_dict = {"priority": priority,
                       "actions": actions,
                       "node": {"id": node_id, "type": node_type},
                       "installInHw": installInHw,
                       "name": name
                       }
        if nwSrc:
            return_dict["nwSrc"] = nwSrc
        if nwDst:
            return_dict["nwDst"] = nwDst
        if etherType:
            return_dict["etherType"] = etherType
        return return_dict


    def create_resource(self, service_uri, resource_path, object_name,
                        object_data):
        """Create a resource of flow entry"""
        return self._resource_operation(service_uri,
                                        'POST',
                                        resource_path,
                                        object_name=object_name,
                                        object_data=object_data)

    def retrieve_resource(self, service_uri, resource_path, parse_response=True):
        """Retrieve a resource of NetScaler Control Center."""
        return self._resource_operation(service_uri, 'GET', resource_path)

    def update_resource(self, service_uri, resource_path, object_name,
                        object_data):
        """Update a resource of the NetScaler Control Center."""
        return self._resource_operation(service_uri,
                                        'PUT',
                                        resource_path,
                                        object_name=object_name,
                                        object_data=object_data)

    def remove_resource(self, service_uri, resource_path, parse_response=True):
        """Remove a resource of NetScaler Control Center."""
        return self._resource_operation(service_uri, 'DELETE', resource_path)

    def _resource_operation(self, service_uri, method, resource_path,
                            object_name=None, object_data=None):
        resource_uri = "%s/%s" % (service_uri, resource_path)
        headers = self._setup_req_headers()
        request_body = None
        if object_data:
            if isinstance(object_data, str):
                request_body = object_data
            else:
                obj_dict = {object_name: object_data}
                request_body = jsonutils.dumps(obj_dict)

        response_status, resp_dict = self._execute_request(method,
                                                           resource_uri,
                                                           headers,
                                                           body=request_body)
        return response_status, resp_dict

    def _is_valid_response(self, response_status):
        # when status is less than 400, the response is fine
        return response_status < requests.codes.bad_request

    def _setup_req_headers(self):
        headers = {ACCEPT_HEADER: JSON_CONTENT_TYPE,
                   CONTENT_TYPE_HEADER: JSON_CONTENT_TYPE,
                   #DRIVER_HEADER: DRIVER_HEADER_VALUE,
                   #TENANT_HEADER: tenant_id,
                   AUTH_HEADER: self.auth}
        return headers

    def _get_response_dict(self, response):
        response_dict = {'status': response.status_code,
                         'body': response.text,
                         'headers': response.headers}
        if self._is_valid_response(response.status_code):
            if response.text:
                #response_dict['dict'] = response.json()
                response_dict['dict'] = response
        return response_dict

    def _execute_request(self, method, resource_uri, headers, body=None):
        response = requests.request(method, url=resource_uri, headers=headers,
                                    data=body)
        #print "response : %s" % response
        #time.sleep(15)
        """
        try:
            response = requests.request(method, url=resource_uri,
                                        headers=headers, data=body)
        except requests.exceptions.ConnectionError:
            msg = (_("Connection error occurred while connecting to %s") %
                   self.service_uri)
            LOG.exception(msg)
            raise NCCException(NCCException.CONNECTION_ERROR)
        except requests.exceptions.SSLError:
            msg = (_("SSL error occurred while connecting to %s") %
                   self.service_uri)
            LOG.exception(msg)
            raise NCCException(NCCException.CONNECTION_ERROR)
        except requests.exceptions.Timeout:
            msg = _("Request to %s timed out") % self.service_uri
            LOG.exception(msg)
            raise NCCException(NCCException.CONNECTION_ERROR)
        except (requests.exceptions.URLRequired,
                requests.exceptions.InvalidURL,
                requests.exceptions.MissingSchema,
                requests.exceptions.InvalidSchema):
            msg = _("Request did not specify a valid URL")
            LOG.exception(msg)
            raise NCCException(NCCException.REQUEST_ERROR)
        except requests.exceptions.TooManyRedirects:
            msg = _("Too many redirects occurred for request to %s")
            LOG.exception(msg)
            raise NCCException(NCCException.REQUEST_ERROR)
        except requests.exceptions.RequestException:
            msg = (_("A request error while connecting to %s") %
                   self.service_uri)
            LOG.exception(msg)
            raise NCCException(NCCException.REQUEST_ERROR)
        except Exception:
            msg = (_("A unknown error occurred during request to %s") %
                   self.service_uri)
            LOG.exception(msg)
            raise NCCException(NCCException.UNKNOWN_ERROR)"""
        resp_dict = self._get_response_dict(response)
#         LOG.debug(_("Response: %s"), resp_dict['body'])
        response_status = resp_dict['status']
        """
        if response_status == requests.codes.unauthorized:
            LOG.exception(_("Unable to login. Invalid credentials passed."
                          "for: %s"), self.service_uri)
            raise NCCException(NCCException.RESPONSE_ERROR)
        if not self._is_valid_response(response_status):
            msg = (_("Failed %(method)s operation on %(url)s "
                   "status code: %(response_status)s") %
                   {"method": method,
                    "url": resource_uri,
                    "response_status": response_status})
            LOG.exception(msg)
            raise NCCException(NCCException.RESPONSE_ERROR)
        """
        return response_status, resp_dict




