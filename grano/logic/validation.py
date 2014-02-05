import re
import colander
from colander import Invalid

from grano.core import db
from grano.model import Schema, Attribute


database_name = colander.Regex('^[a-zA-Z][a-zA-Z0-9_]+[a-zA-Z0-9]$')


def check_attributes(form, value):
    """ Form validator to check that the all attribute names used 
    by this schema are unused. """

    if value.get('obj') == 'relation':
        return

    for attr in value.get('attributes', []):
        q = db.session.query(Attribute)
        q = q.filter(Attribute.name==attr.get('name'))
        q = q.join(Schema)
        q = q.filter(Schema.obj==value.get('obj'))
        q = q.filter(Schema.name!=value.get('name'))
        attrib = q.first()
        if attrib is not None:
            raise Invalid(form,
                "Attribute '%s' already declared in schema '%s'" \
                 % (attr.get('name'), attrib.schema.name))


class AttributeValidator(colander.MappingSchema):
    name = colander.SchemaNode(colander.String(),
        validator=database_name)
    label = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=3))
    description = colander.SchemaNode(colander.String(),
        missing='', default='')
    hidden = colander.SchemaNode(colander.Boolean(),
        missing=False)


class Attributes(colander.SequenceSchema):
    attribute = AttributeValidator()


class SchemaValidator(colander.MappingSchema):
    name = colander.SchemaNode(colander.String(),
        validator=database_name)
    label = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=3))
    label_in = colander.SchemaNode(colander.String(),
        missing=None, validator=colander.Length(min=3))
    label_out = colander.SchemaNode(colander.String(),
        missing=None, validator=colander.Length(min=3))
    hidden = colander.SchemaNode(colander.Boolean(),
        missing=False)
    obj = colander.SchemaNode(colander.String(),
        validator=colander.OneOf(['entity', 'relation']))
    attributes = Attributes()


def validate_schema(data):
    schema = SchemaValidator(validator=check_attributes)
    return schema.deserialize(data)


def validate_properties(data):
    pass
