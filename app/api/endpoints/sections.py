# -*- coding: utf-8 -*-

from flask import request, g
from flask_restplus import Namespace, Resource, abort
from .. import auth
from ..serializers.sections import section_resource_model, section_container
from app.models import Section


ns = Namespace('sections', description='Sections related operations')

# ================================================================================================
# ENDPOINTS
# ================================================================================================
#
#   API Sections endpoints
#
# ================================================================================================


@ns.route('/')
class SectionCollection(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(section_container)
    def get(self):
        """
        Return Sections
        """
        if 'campus' not in dir(g.client):
            abort(400, error='You must have campus')

        return {'sections': [s for s in Section.objects(campus=g.client.campus)]}


@ns.route('/<id>')
@ns.response(404, 'Section not found')
class SectionItem(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(section_resource_model)
    def get(self, id):
        """
        Return section
        """
        if 'campus' not in dir(g.client):
            abort(400, error='You must have campus')

        s = Section.objects.get_or_404(id=id)

        if s.campus != g.client.campus:
            abort(400, error='Not authorized')

        return s
