# -*- coding: utf-8 -*-

from flask_restplus import fields
from .nested import user_nested, api


message_post_model = api.model('Message POST model', {
    'content': fields.String(required=True, description='Content')
})

message_minimal_model = api.model('Message minimal model', {
    'id': fields.String(required=True, description='Message ID'),
    'created_at': fields.DateTime(dt_format='iso8601', required=True, description='Created at (iso8601)'),
    'user': fields.Nested(user_nested, required=True, description='User'),
    'content': fields.String(required=True, description='Content')
})

message_container = api.model('Message container', {
    'messages': fields.List(fields.Nested(message_minimal_model), required=True, description='Messages list')
})
