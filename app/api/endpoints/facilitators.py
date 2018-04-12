# -*- coding: utf-8 -*-

from flask import request
from flask_restplus import Namespace, Resource, abort
from .. import auth
from ..serializers.facilitators import facilitator_container, facilitator_model
from app.models import Facilitator

ns = Namespace('facilitators', description='Facilitators related operation')


# ================================================================================================
# ENDPOINTS
# ================================================================================================
#
#   API facilitators endpoints
#
# ================================================================================================


@ns.route('/')
class FacilitatorCollection(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(facilitator_container)
    def get(self):
        """
        Return Facilitators
        """

        return {'facilitators': [f for f in Facilitator.objects]}


@ns.route('/<id>')
@ns.response(404, 'Facilitator not found')
class FacilitatorItem(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(facilitator_model)
    def get(self, id):
        """
        Return Facilitator
        """
        f = Facilitator.objects.get_or_404(id=id)

        return f
