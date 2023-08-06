from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.orm import class_mapper

relationship_fields = (RelationshipProperty,)


def is_relationship_field(field, model_cls):
    """ Determine if `field` of the `model_cls` is a relational
    field.
    """
    if not model_cls.has_field(field):
        return False
    mapper = class_mapper(model_cls)
    relationships = {r.key: r for r in mapper.relationships}
    field_obj = relationships.get(field)
    return isinstance(field_obj, relationship_fields)


def relationship_cls(field, model_cls):
    """ Return class which is pointed to by relationship field
    `field` from model `model_cls`.

    You have to make sure field exists and is a relationship
    field by yourself. Use `is_relationship_field` for these purposes.
     """
    mapper = class_mapper(model_cls)
    relationships = {r.key: r for r in mapper.relationships}
    field_obj = relationships[field]
    return field_obj.mapper.class_
