# -*- coding: utf-8 -*-

from flask_restplus import Namespace, Resource
from .. import api

ns = Namespace('postman', description='Postman documentation.')


# ================================================================================================
# ENDPOINTS
# ================================================================================================
#
#   API postman endpoints
#
# ================================================================================================

@ns.route('/')
class PostmanResource(Resource):

    def get(self):
        """
        Get Postman documentation
        """
        urlvars = False
        swagger = True
        data = api.as_postman(urlvars=urlvars, swagger=swagger)

        return data
