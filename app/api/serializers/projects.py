# -*- coding: utf-8 -*-

from flask_restplus import fields
from .nested import file_nested
from .. import api


project_minimal_model = api.model('Project minimal model', {
    'id': fields.String(required=True, description='Project ID'),
    'name': fields.String(required=True, description='Project name')
})

project_resource_model = api.inherit('Project resource model', project_minimal_model, {
    'files': fields.List(fields.Nested(file_nested), required=True, description='Files list')
})

project_container = api.model('Project container', {
    'projects': fields.List(fields.Nested(project_minimal_model), required=True, description='Projects list')
})