# -*- coding: utf-8 -*-

from flask_restplus import fields
from .nested import file_nested, api


campus_minimal_model = api.model('Campus minimal model', {
    'id': fields.String(required=True, description='Campus ID'),
    'name': fields.String(required=True, description='Campus name'),
})

campus_model = api.model('Campus model', {
    'files': fields.List(fields.Nested(file_nested), required=True, description='Files list')
})

campus_container = api.model('Campus container', {
    'campus': fields.List(fields.Nested(campus_minimal_model), required=True, description='Campus list')
})
