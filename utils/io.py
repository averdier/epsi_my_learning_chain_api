# -*- coding: utf-8 -*-


def get_name_without_extension(filename):
    """
    Return name of file

    :param filename: Filename
    :type filename: str
    :return: Name of file
    :rtype: str
    """
    name = ''
    if '.' in filename:
        name = filename.rsplit('.', 1)[0].lower()
    return name


def get_extension(filename):
    """
    Return extension of file

    :param filename: Filename
    :type filename: str
    :return: Extension of filename
    :rtype: str
    """
    extension = ''
    if '.' in filename:
        extension = filename.rsplit('.', 1)[1].lower()
    return extension


def allowed_file(config, filename):
    """
    Determine if file is allowed

    :param filename: Filename with extension
    :type filename: str
    :param config: Configuration object
    :type config: object
    :return:
    :rtype: bool
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config