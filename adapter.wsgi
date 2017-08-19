import os
import sys
sys.path.append('/var/www/appremessa')

os.chdir(os.path.dirname(__file__))

import bottle
import app

application = bottle.default_app()
