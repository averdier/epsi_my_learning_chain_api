# -*- coding: utf-8 -*-

from flask_restplus import fields
from .. import api


project_resource_model = api.model('Project resource model', {
    'id': fields.String(required=True, description='Project ID'),
    'name': fields.String(required=True, description='Project name')
})

project_container = api.model('Project container', {
    'projects': fields.List(fields.Nested(project_resource_model), required=True, description='Projects list')
})