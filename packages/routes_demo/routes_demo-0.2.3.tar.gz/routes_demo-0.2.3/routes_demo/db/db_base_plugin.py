import abc

import six




@six.add_metaclass(abc.ABCMeta)
class PardnetPluginBase(object):
    
    @abc.abstractmethod
    def get_controllers(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_controller(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_controller(self, context, controller):
        pass

    @abc.abstractmethod
    def update_controller(self, context, id, controller):
        pass

    @abc.abstractmethod
    def delete_controller(self, context, id):
        pass
    
    
    
    @abc.abstractmethod
    def get_switches(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_switch(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_switch(self, context, switch):
        pass

    @abc.abstractmethod
    def update_switch(self, context, id, switch):
        pass

    @abc.abstractmethod
    def delete_switch(self, context, id):
        pass
    
    
    
    @abc.abstractmethod
    def get_haproxies(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_haproxy(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_haproxy(self, context, haproxy):
        pass

    @abc.abstractmethod
    def update_haproxy(self, context, id, haproxy):
        pass

    @abc.abstractmethod
    def delete_haproxy(self, context, id):
        pass
    
    
    
    
    
    
    
