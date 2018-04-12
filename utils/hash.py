# -*- coding: utf-8 -*-

import hashlib


def create_account_filename(seed):
    """
    Create account filename from seed
    :param seed:
    :return:
    """
    seed_hash = create_seed_hash(seed)
    filename = seed_hash[:12]
    filename += ".json"
    return filename


def create_seed_hash(seed):
    """
    Create SHA256 hash of seed

    :param seed: Seed
    :return: SHA256 hash of seed
    """
    s = hashlib.sha256(seed.encode('utf-8'))
    return s.hexdigest()


def get_checksum(address, seed):
    """
    Create checksum of address + seed

    :param address:
    :param seed:
    :return: Checksum of address + seed
    """
    data = address + seed
    s = hashlib.sha256(data.encode('utf-8'))
    return s.hexdigest()


def verify_checksum(checksum, address, seed):
    """
    Verify checksum of address + seed

    :param checksum:
    :param address:
    :param seed:
    :return: True if get_checksum(address, seed), else False
    """
    actual_checksum = get_checksum(address, seed)
    if actual_checksum == checksum:
        return True
    else:
        return False