# -*- coding: utf-8 -*-

from flask_restplus import fields
from .nested import facilitator_nested, api


offer_post_model = api.model('Offer POST model', {
    'name': fields.String(required=True, min_length=4, description='Name'),
    'tags': fields.List(fields.String(), required=False, description='Tags'),
    'price': fields.Integer(required=True, min=0, description='Price'),
    'description': fields.String(required=False, description='Description')
})

offer_patch_model = api.model('Offer PATCH model', {
    'name': fields.String(required=False, min_length=4, description='Name'),
    'tags': fields.List(fields.String(), required=False, description='Tags'),
    'price': fields.Integer(required=False, min=0, description='Price'),
    'description': fields.String(required=False, description='Description')
})

offer_minimal_model = api.model('Offer minimal model', {
    'id': fields.String(required=True, description='Offer ID'),
    'facilitator_id': fields.String(required=True, description='Facilitator ID', attribute=lambda o: o.facilitator.id),
    'name': fields.String(required=True, description='Name'),
    'tags': fields.List(fields.String(), required=True, description='Tags'),
    'price': fields.Integer(required=True, description='Price')
})

offer_model = api.inherit('Offer model', offer_minimal_model, {
    'description': fields.String(required=True, description='Description'),
    'facilitator': fields.Nested(facilitator_nested, required=True, description='Facilitator')
})


offer_container = api.model('Offer container', {
    'offers': fields.List(fields.Nested(offer_minimal_model), required=True, description='Offers list')
})