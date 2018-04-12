# -*- coding: utf-8 -*-

from flask import request, g, current_app
from flask_restplus import Namespace, Resource, abort
from .. import auth
from ..serializers.offers import offer_container, offer_post_model, offer_patch_model, offer_model
from ..serializers.claims import claim_container, claim_model, claim_post_model, claim_put_model
from ..serializers.messages import message_container, message_post_model, message_minimal_model
from app.models import Offer, Claim, Group, Facilitator, Message
from utils.iota import make_transfer
from utils.email import send_mail_with_service

ns = Namespace('offers', description='Offers related operations')


# ================================================================================================
# ENDPOINTS
# ================================================================================================
#
#   API Offers endpoints
#
# ================================================================================================


@ns.route('/')
class OfferCollection(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(offer_container)
    def get(self):
        """
        Return Offers
        """
        return {'offers': [o for o in Offer.objects]}

    @ns.marshal_with(offer_model)
    @ns.expect(offer_post_model)
    def post(self):
        """
        Add Offer
        """
        data = request.json

        if g.client.type != 'facilitator':
            abort(400, error='You must be facilitator')

        f = Facilitator.objects.get_or_404(id=g.client.id)

        if Offer.objects(name=data['name']).count() > 0:
            abort(400, error='Name already exist')

        o = Offer(
            facilitator=f,
            name=data['name'],
            tags=data.get('tags'),
            price=data['price'],
            description=data.get('description')
        )

        o.save()

        return o


@ns.route('/<id>')
@ns.response(404, 'Offer not found')
class OfferItem(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(offer_model)
    def get(self, id):
        """
        Return Offer
        """
        o = Offer.objects.get_or_404(id=id)

        return o

    @ns.response(204, 'Offer successfully patched')
    @ns.expect(offer_patch_model)
    def patch(self, id):
        """
        Patch Offer
        """
        data = request.json
        o = Offer.objects.get_or_404(id=id)

        if o.facilitator.id != g.client.id:
            abort(400, error='Not authorized')

        if len(data) == 0:
            abort(400, error='No data')

        if data.get('name'):
            os = Offer.objects(name=data['name']).first()

            if os is not None and os.id != o.id:
                abort(400, error='Name already exist')

            o.name = data['name']

        if data.get('tags'):
            o.tags = data['tags']

        if data.get('price'):
            o.price = data['price']

        if data.get('description'):
            o.description = data['description']

        o.save()

        return 'Offer successfully patched', 204

    @ns.response(204, 'Offer successfully deleted')
    def delete(self, id):
        """
        Delete Offer
        """
        o = Offer.objects.get_or_404(id=id)

        if o.facilitator.id != g.client.id:
            abort(400, error='Not authorized')

        o.delete()

        return 'Offer successfully deleted', 204


@ns.route('/<id>/claims')
@ns.response(404, 'Offer not found')
class OfferClaimCollection(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(claim_container)
    def get(self, id):
        """
        Return Claims of Offer
        """
        o = Offer.objects.get_or_404(id=id)

        return {'claims': [c for c in Claim.objects(offer=o)]}

    @ns.marshal_with(claim_model)
    @ns.expect(claim_post_model)
    def post(self, id):
        """
        Add Claim
        """
        data = request.json
        o = Offer.objects.get_or_404(id=id)

        gr = Group.objects.get_or_404(id=data['group'])

        if gr.balance - gr.reserved < o.price:
            abort(400, error='No founds')

        c = Claim(
            offer=o,
            group=gr,
            status='pending',
            message=data.get('message', '')
        )
        c.save()

        gr.reserved += o.price
        gr.save()

        try:
            send_mail_with_service({
                'server': current_app.config['EMAIL_HOST'],
                'recipients': [o.facilitator.email],
                'subject': '{0} | Demande'.format(o.name),
                'body': "Bonjour \n\nLe groupe {0} souhaiterait votre intervention \nMessage:\n{1}".format(gr.name, c.message)
            })
        except Exception as ex:
            current_app.logger.error(ex)

        return c


@ns.route('/<id>/claims/<cid>')
@ns.response(404, 'Claim not found')
class OfferClaimItem(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(claim_model)
    def get(self, id, cid):
        """
        Return Claim
        """
        o = Offer.objects.get_or_404(id=id)
        c = Claim.objects.get_or_404(id=cid)

        if c.offer.id != o.id:
            abort(400, error='Impossible')

        return c

    @ns.response(204, 'Claim successfully updated')
    @ns.expect(claim_put_model)
    def put(self, id, cid):
        """
        Update claim
        """
        o = Offer.objects.get_or_404(id=id)
        c = Claim.objects.get_or_404(id=cid)

        if c.offer.id != o.id:
            abort(400, error='Impossible')

        if c.offer.facilitator.id != g.client.id:
            abort(400, error='Not authorized')

        if c.status in ['canceled', 'validated']:
            abort(400, error='Already closed')

        data = request.json

        if data['status'] not in ['running', 'canceled', 'validated']:
            abort(400, error='Unknown type')

        recipients = [o.facilitator.email]
        for s in c.group.students:
            recipients.append(s.email)

        payload = {
            'server': current_app.config['EMAIL_HOST'],
            'recipients': recipients,
            'subject': '{0} | '.format(o.name),
            'body': "Bonjour \n\n"
        }

        if data['status'] == 'canceled':
            c.group.reserved -= o.price
            c.group.save()
            payload['subject'] += 'Annulation'
            payload['body'] += "Annulation de la demande d'intervention"

        if data['status'] == 'validated':
            make_transfer(current_app.config['IOTA_HOST'], {
                'recipient_address': o.facilitator.deposit_address.address,
                'message': 'From EPSI',
                'tag': 'OFFERVALIDATED',
                'value': o.price,
                'seed': c.group.seed,
                'deposit_address': c.group.deposit_address.address
            })
            c.group.reserved -= o.price
            c.group.save()
            payload['subject'] += 'Cloture'
            payload['body'] += "Cloture de l'intervention, merci d'avoir utilisé notre service"

        c.status = data['status']

        c.save()

        try:
            send_mail_with_service(payload)
        except Exception as ex:
            current_app.logger.error(ex)

        return 'Claim successfully update', 204

    @ns.response(204, 'Claim successfully deleted')
    def delete(self, id, cid):
        """
        Delete Claim
        """
        o = Offer.objects.get_or_404(id=id)
        c = Claim.objects.get_or_404(id=cid)

        if c.offer.id != o.id:
            abort(400, error='Impossible')

        if c.status != 'validated':
            c.group.reserved -= o.price
            c.group.save()

        c.delete()

        return 'Claim successfully deleted', 204


@ns.route('/<id>/claims/<cid>/messages')
@ns.response(404, 'Claim not found')
class OfferClaimMessage(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(message_container)
    def get(self, id, cid):
        """
        Get messages
        """
        o = Offer.objects.get_or_404(id=id)
        c = Claim.objects.get_or_404(id=cid)

        if c.offer.id != o.id:
            abort(400, error='Impossible')

        return {'messages': [m for m in Message.objects(claim=c)]}

    @ns.marshal_with(message_minimal_model)
    @ns.expect(message_post_model)
    def post(self, id, cid):
        """
        Add message
        """
        o = Offer.objects.get_or_404(id=id)
        c = Claim.objects.get_or_404(id=cid)

        if c.offer.id != o.id:
            abort(400, error='Impossible')

        data = request.json

        m = Message(
            claim=c,
            user=g.client,
            content=data['content']
        )
        m.save()

        return m
