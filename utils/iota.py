# -*- coding: utf-8 -*-

from iota import Iota, Address, ProposedTransaction, TryteString, Tag
import secrets
import string


def generate_seed():
    """
    Generate random IOTA Seed
    :return:
    """
    return ''.join(secrets.choice(string.ascii_uppercase + "9") for _ in range(81))


def convert_units(value, unit):
    """
    Convert IOTA units

    :param value:
    :param unit:
    :return:
    """
    value = float(value)

    if unit == "i":
        value = str(int(value)) + "i"
        return value

    elif unit == "ki":
        value = '{0:.3f}'.format(value / 1000)
        value = str(value + "Ki")
        return value

    elif unit == "mi":
        value = '{0:.6f}'.format(value / 1000000)
        value = str(value) + "Mi"
        return value

    elif unit == "gi":
        value = '{0:.9f}'.format(value / 1000000000)
        value = str(value + "Gi")
        return value

    elif unit == "ti":
        value = '{0:.12f}'.format(value / 1000000000000)
        value = str(value + "Ti")
        return value


def address_checksum(address):
    """
    Takes a address (81 Characters) and converts it to an address with checksum (90 Characters)

    :param address:
    :return:
    """
    bytes_address = bytes(address.encode('utf-8'))
    addy = Address(bytes_address)
    address = str(addy.with_valid_checksum())
    return address


def is_valid_address(address_with_checksum):
    """
    Takes an address with checksum and verifies if the address matches with the checksum

    :param address_with_checksum:
    :return:
    """
    address = address_with_checksum[:81]
    new_address_with_checksum = address_checksum(address)
    if new_address_with_checksum == address_with_checksum:
        return True
    else:
        return False


def address_balance(iota_node, address):
    """
    Sends a request to the IOTA node and gets the current confirmed balance

    :param iota_node:
    :param address:
    :return:
    """
    api = Iota(iota_node)
    gna_result = api.get_balances([address])
    balance = gna_result['balances']
    return balance[0]


def make_transfer(iota_node, args):
    """
    Make transfers

    :param iota_node:
    :param args:
    :return:
    """
    txn = [ProposedTransaction(
        address=Address(Address(bytes(args['recipient_address'].encode('utf-8')))),
        message=TryteString.from_string(args['message']),
        tag=Tag(args['tag']),
        value=args['value']
    )]
    api = Iota(iota_node, args['seed'])
    r = api.send_transfer(
        depth=7,
        transfers=txn,
        change_address=Address(bytes(args['deposit_address'].encode('utf-8'))),
        min_weight_magnitude=13
    )
    print(r)
