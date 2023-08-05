__author__ = 'calvin'

import copy


class Property(object):
    def __init__(self, default_value):
        self.instances = {}
        self.default_value = default_value
        self.value = copy.deepcopy(default_value)

    def __get__(self, obj, objtype=None):
        return obj.event_dispatcher_properties[self.name]['value']

    def __set__(self, obj, value):
        if value != obj.event_dispatcher_properties[self.name]['value']:
            obj.event_dispatcher_properties[self.name]['value'] = value
            obj.dispatch(self.name, obj, value)

    def __delete__(self, obj):
        raise AttributeError("Cannot delete properties")

    def register(self, instance, property_name, default_value, **kwargs):
        info = {'property': self, 'value': default_value, 'name': property_name, 'callbacks': []}
        info.update(kwargs)
        # Create the instances dictionary at registration so that each class has it's own instance of it.
        self.instances[instance] = info
        if not hasattr(instance, 'event_dispatcher_properties'):
            instance.event_dispatcher_properties = {}
        instance.event_dispatcher_properties[property_name] = info

    def get_dispatcher_property(self, property_name):
        return self.instances[self][property_name]


