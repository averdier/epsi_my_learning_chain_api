# -*- coding: utf-8 -*-

from flask import request, g
from flask_restplus import Namespace, Resource, abort
from .. import auth
from ..serializers.projects import project_resource_model, project_container
from app.models import Project, Student, Group

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
        if g.client.type != 'student':
            abort(400, error='Not authorized')
        s = Student.objects.get_or_404(id=g.client.id)

        result = []
        for gr in s.groups:
            result.append(gr.project)

        return {'projects': result}


@ns.route('/<id>')
@ns.response(404, 'Project not found')
class ProjectItem(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(project_resource_model)
    def get(self, id):
        """
        Return Project
        """
        p = Project.objects.get_or_404(id=id)

        if g.client.type == 'student':
            s = Student.objects.get_or_404(id=g.client.id)

            grs = Group.objects(project=p, students__contains=s)
            if len(grs) == 0:
                abort(400, error='Not authorized')

        elif g.client != 'facilitator':
            abort(400, error='Not authorized')

        return p
