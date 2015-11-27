#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
reload(sys)
sys.setdefaultencoding("utf-8")


logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/restaurant_py/")

activate_this = '/var/www/restaurant_py/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from utf8_error_solve import app as application
application.secret_key = 'Add your secret key'
