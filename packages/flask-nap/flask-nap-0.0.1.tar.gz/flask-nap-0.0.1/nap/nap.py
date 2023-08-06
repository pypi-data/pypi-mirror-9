import datetime
import json
from collections import OrderedDict
from sqlalchemy.orm import joinedload

def _json_repr(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    return obj

class ModelSerializer(object):

    @classmethod
    def valid(cls, data):
        has_required_fields = not set(cls.required) - set(data)
        only_allowed_fields = set(data) - set(cls.read_only) == set(data)
        too_many_fields     = set(data) - set(cls.model.__table__.columns.keys())

        if has_required_fields and only_allowed_fields and not too_many_fields:
            return True

        return False

    @classmethod
    def deserialize(cls, model=None, **kwargs):
        model = cls.model() if model is None else model
        columns = model.__table__.columns.keys()

        if not cls.valid(kwargs):
            return

        for key in kwargs:
            setattr(model, key, kwargs[key])

        return model

    @classmethod
    def _serialize(cls, queryset):
        serialized = []

        fields = cls.model.__table__.columns.keys()
        relation_serializers = cls.relation_serializers if hasattr(cls, 'relation_serializers') else {}

        queryset = queryset if isinstance(queryset, list) else [queryset]
        for row in queryset:
            serialized_row = {}

            for field in fields:
                row_field = getattr(row, field)
                serialized_row[field] = _json_repr(row_field)

            for relation in relation_serializers:
                row_field = getattr(row, relation)
                relation_serializer = relation_serializers[relation]
                serialized_row[relation] = relation_serializer._serialize(row_field)

            serialized.append(serialized_row)
        return serialized

    @classmethod
    def serialize(cls, filters={}):
        return cls._serialize(cls.queryset(**filters))

    @classmethod
    def queryset(cls, **kwargs):
        nested_relationships = cls.nested_relationships()
        queryset = cls.model.query
        if nested_relationships:
            queryset = queryset.options(joinedload(*nested_relationships))
        return queryset.filter_by(**kwargs).all()

    @classmethod
    def nested_relationships(cls, relationships=None):
        relationships = [] if relationships is None else relationships

        nested_relationships = cls.relation_serializers if hasattr(cls, 'relation_serializers') else {}
        if nested_relationships:
            for name in nested_relationships:
                relationships.append(name)
                nested_relationships[name].nested_relationships(relationships)

        return relationships
