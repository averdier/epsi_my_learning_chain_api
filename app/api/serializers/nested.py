# -*- coding: utf-8 -*-

from flask_restplus import fields
from .. import api


campus_nested = api.model('Campus nested', {
    'id': fields.String(required=True, description='Campus ID'),
    'name': fields.String(required=True, description='Campus name')
})

project_nested = api.model('Project nested', {
    'id': fields.String(required=True, description='Project ID'),
    'name': fields.String(required=True, description='Project name')
})

group_nested = api.model('Group nested', {
    'id': fields.String(required=True, description='Group ID'),
    'name': fields.String(required=True, description='Group name'),
    'project_id': fields.String(required=True, description='Group project', attribute=lambda g: g.project.id),
    'students_count': fields.Integer(required=True, description='User count', attribute=lambda g: len(g.students))
})


offer_nested = api.model('Offer nested', {
    'id': fields.String(required=True, description='Offer ID'),
    'facilitator_id': fields.String(required=True, description='Facilitator ID', attribute=lambda o: o.facilitator.id),
    'name': fields.String(required=True, description='Name'),
    'tags': fields.List(fields.String(), required=True, description='Tags'),
    'price': fields.Integer(required=True, description='Price')
})


student_nested = api.model('Student nested', {
    'id': fields.String(required=True, description='Student ID'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='First name'),
    'img_uri': fields.String(required=True, description='Img uri')
})

user_nested = api.inherit('User nested', student_nested, {
    'type': fields.String(required=True, description='Type')
})

facilitator_nested = api.inherit('Facilitator model', student_nested, {})


file_nested = api.model('File nested', {
    'id': fields.String(required=True, description='File ID'),
    'name': fields.String(required=True, description='Filename'),
    'extension': fields.String(required=True, description='Extension')
})

claim_nested = api.model('Claim nested', {
    'id': fields.String(required=True, description='Claim ID'),
    'offer_id': fields.String(required=True, description='Offer ID', attribute=lambda c: c.offer.id),
    'status': fields.String(required=True, description='Status')
})
