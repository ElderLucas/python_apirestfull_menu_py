activate_this = '/var/www/restaurant_py/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from project import app as application
