# -*- coding: utf-8 -*-


class Config:
    """
    Base configuration
    """
    SECRET_KEY = 'default'

    PRIVATE_KEY = ""
    PUBLIC_KEY = ""

    MONGODB_DB = ''
    MONGODB_HOST = ''
    MONGODB_CONNECT = False

    IOTA_HOST = ""
    EMAIL_HOST = ""
    UPLOAD_BASE = ""

    RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTPLUS_VALIDATE = True
    RESTPLUS_MASK_SWAGGER = False

    @staticmethod
    def init_app(app):
        """
        Init app
        :param app: Flask App
        :type app: Flask
        """
        with open(app.config['PRIVATE_KEY']) as f:
            app.config['PRIVATE_KEY'] = f.read()

        with open(app.config['PUBLIC_KEY']) as f:
            app.config['PUBLIC_KEY'] = f.read()


class DevelopmentConfig(Config):
    """
    Development configuration
    """
    pass


class ProductionConfig(Config):
    """
    Production configuration
    """
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

