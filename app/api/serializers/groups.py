# -*- coding: utf-8 -*-

from flask_restplus import fields
from .nested import project_nested, campus_nested, student_nested, file_nested, claim_nested, api


group_minimal_model = api.model('Group minimal model', {
    'id': fields.String(required=True, description='Group ID'),
    'name': fields.String(required=True, description='Group name'),
    'project_id': fields.String(required=True, description='Group project', attribute=lambda g: g.project.id),
    'students_count': fields.Integer(required=True, description='User count', attribute=lambda g: len(g.students))
})

group_model = api.inherit('Group resource model', group_minimal_model, {
    'id': fields.String(required=True, description='Group ID'),
    'name': fields.String(required=True, description='Group name'),
    'project': fields.Nested(project_nested, required=True, description='Group project'),
    'campus': fields.Nested(campus_nested, attribute=lambda g: g.project.campus, description='Group campus'),
    'students': fields.List(fields.Nested(student_nested), required=True, description='Students list'),
    'balance': fields.Integer(required=True, description='Balance'),
    'reserved': fields.Integer(required=True, description='Reserved'),
    'files': fields.List(fields.Nested(file_nested), required=True, description='Files list'),
    'claims': fields.List(fields.Nested(claim_nested), required=True, description='Claims list')
})

group_container = api.model('Group container', {
    'groups': fields.List(fields.Nested(group_minimal_model), required=True, description='Groups list')
})

