# -*- coding: utf-8 -*-

from flask import request, g, current_app
from flask_restplus import Namespace, Resource, abort
from .. import auth
from ..serializers.campus import campus_model, campus_container
from app.models import Campus

ns = Namespace('campus', description='Campus related operation')


# ================================================================================================
# ENDPOINTS
# ================================================================================================
#
#   API campus endpoints
#
# ================================================================================================


@ns.route('/')
class CampusCollection(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(campus_container)
    def get(self):
        """
        Return Campus
        """
        return {'campus': [c for c in Campus.objects]}


@ns.route('/<id>')
@ns.response(404, 'Campus not found')
class CampusItem(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(campus_model)
    def get(self, id):
        """
        Return Campus
        """
        c = Campus.objects.get_or_404(id=id)

        return c
