# -*- coding: utf-8 -*-

import os
from configobj import ConfigObj
from app import create_app


conf_path = os.environ.get('APP_SETTINGS')
if not conf_path:
    raise Exception('Unable to find APP_SETTINGS.')

conf = ConfigObj(conf_path)
config_name = conf.get('CONFIG', 'default')

app = create_app(config_name)


if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5552'))
    except ValueError:
        PORT = 5551

    app.run(HOST, PORT, debug=True) # On Windows
    #app.run(HOST, PORT, debug=True, processes=3) # On Linux
    #app.run('0.0.0.0', 8000, processes=3) # On docker
