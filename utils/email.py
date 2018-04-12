# -*- coding: utf-8 -*-

import requests


def send_mail_with_service(args):
    """
    Send mail with service

    :param args:
    :return:
    """
    payload = {
        'recipients': args['recipients'],
        'template': args.get('template', 'default'),
        'subject': args['subject'],
        'body': args['body']
    }

    response = requests.post(args['server'] + '/send/', json=payload)

    if response.status_code != 200:
        return False

    return True
