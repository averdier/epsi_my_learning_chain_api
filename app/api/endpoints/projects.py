# -*- coding: utf-8 -*-

from flask import request, g
from flask_restplus import Namespace, Resource, abort
from .. import auth
from ..serializers.projects import project_resource_model, project_container
from app.models import Project

ns = Namespace('projects', description='Projects related operations')


# ================================================================================================
# ENDPOINTS
# ================================================================================================
#
#   API Projects endpoints
#
# ================================================================================================


@ns.route('/')
class ProjectCollection(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(project_container)
    def get(self):
        """
        Return Projects
        """
        if 'campus' not in dir(g.client):
            abort(400, error='You must have campus')

        return {'projects': [p for p in Project.objects(campus=g.client.campus)]}


@ns.route('/<id>')
@ns.response(404, 'Project not found')
class ProjectItem(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(project_resource_model)
    def get(self, id):
        """
        Return Project
        """
        if 'campus' not in dir(g.client):
            abort(400, error='You must have campus')

        p = Project.objects.get_or_404(id=id)

        if p.campus != g.client.campus:
            abort(400, error='Not authorized')

        return p
