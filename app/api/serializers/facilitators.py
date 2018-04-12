# -*- coding: utf-8 -*-

from flask_restplus import fields
from .. import api


facilitator_offer_nested = api.model('Facilitator offer nested', {
    'id': fields.String(required=True, description='Offer ID'),
    'name': fields.String(required=True, description='Name'),
    'tags': fields.List(fields.String(), required=True, description='Tags'),
    'price': fields.Integer(required=True, description='Price')
})

facilitator_minimal_model = api.model('Facilitator minimal model', {
    'id': fields.String(required=True, description='Facilitator ID'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='First name'),
    'img_uri': fields.String(required=True, description='Img uri'),
    'tags': fields.List(fields.String(), required=True, description='Tags')
})

facilitator_model = api.inherit('Facilitator model', facilitator_minimal_model, {
    'email': fields.String(required=True, description='Email'),
    'offers': fields.List(fields.Nested(facilitator_offer_nested), required=True, description='Offers list')
})


facilitator_container = api.model('Facilitator container', {
    'facilitators': fields.List(fields.Nested(facilitator_minimal_model), required=True, description='Facilitators list')
})
