class Encodable:
    _encode_attrs = tuple()
    _map = {}
    _table = tuple()

    def to_dict(self):
        d = {}
        for attr_name in self._encode_attrs:
            d[attr_name] = getattr(self, attr_name)

        return d

    @classmethod
    def from_dict(cls, d):
        inst = cls()
        for attr in cls._map:
            setattr(inst, cls._map[attr], d.get(attr))

        for attr_name in cls._encode_attrs:
            setattr(inst, d[attr_name])

        return inst

    @classmethod
    def fields(cls):
        return sorted(cls._map.values())

    @classmethod
    def table_fields(cls):
        return cls._table

    def row(self):
        return [getattr(self, name) for name in self._table]

    def __repr__(self):
        cls_name = self.__class__.__name__
        attr_reprs = []
        for name in self._map.values():
            attr_reprs.append('%s=%r' % (name, getattr(self, name)))

        return '%s(%s)' % (cls_name, ', '.join(attr_reprs))


def decode_list(cls, lst):
    decoded_list = []
    for entry in lst:
        decoded_list.append(cls.from_dict(entry))
    return decoded_list


def decode_dict(cls, d, key_attr_name=None):
    decoded_list = []
    for key in d:
        inst = cls.from_dict(d[key])
        if key_attr_name:
            setattr(inst, key_attr_name, key)
        decoded_list.append(inst)

    return decoded_list
