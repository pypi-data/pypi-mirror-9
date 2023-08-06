from flatland.util import symbol

deleted = symbol('deleted')


class _TypeLookup(object):
    __slots__ = 'base', 'map', 'descriptor_id'

    def __init__(self, cls, descriptor):
        self.base = cls
        self.map = descriptor.map
        self.descriptor_id = id(descriptor)

    def __getitem__(self, key):
        for frame in self._frames():
            try:
                value = frame[key]
            except KeyError:
                pass
            else:
                if value is deleted:
                    raise KeyError(key)
                return value
        raise KeyError(key)

    def __setitem__(self, key, value):
        self._base_frame[key] = value

    def __delitem__(self, key):
        self[key]  # must exist to delete
        self._base_frame[key] = deleted

    def __contains__(self, key):
        return key in self.iterkeys()

    def copy(self):
        return dict(self.iteritems())

    def clear(self):
        frame = self._base_frame
        for key in frame.keys():
            frame[key] = deleted

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def pop(self, key, *default):
        try:
            current = self[key]
        except KeyError:
            if not default:
                raise KeyError(key)
            return default[0]
        self[key] = deleted
        return current

    def popitem(self):
        raise NotImplementedError()

    def setdefault(self, key, default):
        return self._base_frame.setdefault(key, default)

    def update(self, *iterable, **values):
        simplified = dict(*iterable, **values)
        self._base_frame.update(simplified)

    def iteritems(self):
        seen = set()
        for frame in self._frames():
            for key, value in frame.iteritems():
                if key not in seen:
                    seen.add(key)
                    if value is not deleted:
                        yield (key, value)

    def items(self):
        return list(self.iteritems())

    def iterkeys(self):
        return (item[0] for item in self.iteritems())

    def keys(self):
        return list(self.iterkeys())

    def itervalues(self):
        return (item[1] for item in self.iteritems())

    def values(self):
        return list(self.itervalues())

    def __repr__(self):
        return repr(self.copy())

    def _frames(self):
        for cls in self.base.__mro__:
            member = cls.__dict__.get('properties')
            if cls not in self.map:
                if member is not None and id(member) != self.descriptor_id:
                    continue
                self.map.setdefault(cls, member.initial_set)
            yield self.map[cls]
            if member is not None and id(member) == self.descriptor_id:
                break

    @property
    def _base_frame(self):
        try:
            return self.map[self.base]
        except KeyError:
            pass
        if 'properties' in self.base.__dict__:
            member = self.base.__dict__['properties']
            if id(member) == self.descriptor_id:
                return self.map.setdefault(self.base, member.initial_set)
        return self.map.setdefault(self.base, {})


class _InstanceLookup(object):
    __slots__ = 'local', 'class_lookup'

    def __init__(self, instance, class_lookup):
        try:
            local = instance.__dict__.setdefault('properties', {})
        except AttributeError:
            try:
                local = self.instance.properties
            except AttributeError:
                raise AttributeError(
                    "%s object has no attribute 'properties'" % (
                        instance.__class__))
        self.local = local
        self.class_lookup = class_lookup

    def __getitem__(self, key):
        try:
            value = self.local[key]
        except KeyError:
            pass
        else:
            if value is deleted:
                raise KeyError(key)
            return value
        return self.class_lookup[key]

    def __setitem__(self, key, value):
        self.local[key] = value

    def __delitem__(self, key):
        self[key]  # must exist to delete
        self.local[key] = deleted

    def iteritems(self):
        seen = set()
        for key, value in self.local.iteritems():
            seen.add(key)
            if value is not deleted:
                yield key, value
        for key, value in self.class_lookup.iteritems():
            if key not in seen:
                seen.add(key)
                if value is not deleted:
                    yield key, value

    def copy(self):
        return dict(self.iteritems())

    def __repr__(self):
        return repr(dict(self.copy()))


class Properties(object):

    def __init__(self, **initial_set):
        self.initial_set = initial_set
        self.map = {}

    def __get__(self, instance, cls):
        class_lookup = _TypeLookup(cls, self)
        if instance is None:
            return class_lookup
        return _InstanceLookup(instance, class_lookup)

    def __set__(self, instance, value):
        class_lookup = _TypeLookup(type(instance), self)
        local = _InstanceLookup(instance, class_lookup)
        local.clear()
        local.update(value)


class Sample(object):

    properties = Properties(foo='bar', baz='quux')


class Sub(Sample):
    pass


class Fork(Sample):

    properties = Properties(other='snork')

Sample.properties['sample'] = 'val1'
Sample.properties['shadowed'] = 'shadowed'
Sub.properties['sub'] = 'val2'

del Sub.properties['shadowed']

subi = Sub()
i = Sample()
