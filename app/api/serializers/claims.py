# -*- coding: utf-8 -*-

from flask_restplus import fields
from .nested import group_nested, offer_nested, api

claim_post_model = api.model('Claim POST model', {
    'group': fields.String(required=True, description='Group ID'),
    'message': fields.String(required=False, description='Message')
})

claim_put_model = api.model('Claim PUT model', {
    'status': fields.String(required=True, description='Status')
})


claim_minimal_resource = api.model('Claim minimal model', {
    'id': fields.String(required=True, description='Claim ID'),
    'offer_id': fields.String(required=True, description='Offer ID', attribute=lambda c: c.offer.id),
    'group_id': fields.String(required=True, description='Group ID', attribute=lambda c: c.group.id),
    'status': fields.String(required=True, description='Status')
})

claim_model = api.inherit('Claim model', claim_minimal_resource, {
    'message': fields.String(required=True, description='Message'),
    'group': fields.Nested(group_nested, required=True, description='Group'),
    'offer': fields.Nested(offer_nested, required=True, description='Offer')
})


claim_container = api.model('Claim container', {
    'claims': fields.List(fields.Nested(claim_minimal_resource), required=True, description='Claims list')
})
