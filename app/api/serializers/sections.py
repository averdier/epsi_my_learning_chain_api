# -*- coding: utf-8 -*-

from flask_restplus import fields
from .. import api


section_resource_model = api.model('Section resource model', {
    'id': fields.String(required=True, description='Section ID'),
    'year': fields.Integer(required=True, description='Year of section'),
    'name': fields.String(required=True, description='Section name')
})

section_container = api.model('Section container', {
    'sections': fields.List(fields.Nested(section_resource_model), required=True, description='Sections list')
})