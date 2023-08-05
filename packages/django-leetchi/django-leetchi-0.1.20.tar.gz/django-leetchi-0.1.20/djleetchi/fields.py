from django.db import models

from .api import handler


class ResourceField(models.IntegerField):
    def __init__(self, to=None, *args, **kwargs):
        super(ResourceField, self).__init__(*args, **kwargs)

        self.to = to

    def get_attname(self):
        return '%s_id' % self.name

    def contribute_to_class(self, cls, name):
        super(ResourceField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, ReverseSingleRelatedObjectDescriptor(self))


class ReverseSingleRelatedObjectDescriptor(object):
    def __init__(self, field_with_rel):
        self.field = field_with_rel

    def __get__(self, instance, instance_type=None):

        if instance is None:
            return self

        cache_name = self.field.get_cache_name()
        try:
            return getattr(instance, cache_name)
        except AttributeError:
            val = getattr(instance, self.field.attname)
            if val is None:
                # If NULL is an allowed value, return it.
                if self.field.null:
                    return None

            rel_obj = self.field.to.get(val, handler=handler)

            setattr(instance, cache_name, rel_obj)

            return rel_obj

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError("%s must be accessed via instance" % self._field.name)

        if value is None and self.field.null is False:
            raise ValueError('Cannot assign None: "%s.%s" does not allow null values.' %
                             (instance._meta.object_name, self.field.name))
        elif value is not None and not isinstance(value, self.field.to):
            raise ValueError('Cannot assign "%r": "%s.%s" must be a "%s" instance.' %
                             (value, instance._meta.object_name,
                              self.field.name, self.field.to._meta.object_name))
        val = value.get_pk()

        setattr(instance, self.field.attname, val)

        setattr(instance, self.field.get_cache_name(), value)


try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], ["^djleetchi\.fields\.ResourceField"])
