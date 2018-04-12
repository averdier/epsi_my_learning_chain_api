# -*- coding: utf-8 -*-

from flask import request, send_file, g
from flask_restplus import Namespace, Resource, abort
from .. import auth
from app.models import File, Campus, Project, Group


ns = Namespace('files', description='Files related operation')


# ================================================================================================
# ENDPOINTS
# ================================================================================================
#
#   API files endpoints
#
# ================================================================================================


@ns.route('/<id>')
@ns.response(404, 'File not found')
class FileItem(Resource):
    decorators = [auth.login_required]

    def get(self, id):
        """
        Return file
        """
        f = File.objects.get_or_404(id=id)

        grs = Group.objects(files__contains=f)
        if len(grs) > 0:
            if 'groups' not in dir(g.client):
                abort(400, error='You must have group')

            found = False
            for gr in g.client.groups:
                if gr in grs:
                    if f in gr.files:
                        found = True

            if found:
                return send_file(f.path)
            else:
                abort(400, error='Not authorized')

        else:
            return send_file(f.path)